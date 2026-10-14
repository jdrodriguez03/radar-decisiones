"""Prueba el prompt con 15 estados reales del motor. Dueño: Julian.

Qué hace, caso por caso:
1. Arma el estado real con motor.api.calcular_estado (la misma función que usa la app).
2. Le pide la explicación a la IA, sin caché y sin plantilla: queremos ver lo que escribe la IA.
3. Revisa el texto dos veces: cifras (ia/validador.py) y forma (ia/reglas.py).
   Además dice qué vería el jurado en vivo: el texto de la IA o la plantilla.
4. Guarda todo en docs/textos_ia.json (lo lee tests/test_reglas_ia.py) e imprime
   una tabla en Markdown para pegar en docs/pruebas_ia.md.

Correr desde la raíz del repo, con la llave en .streamlit/secrets.toml o en ANTHROPIC_API_KEY:
    python scripts/probar_ia.py              # los 15 casos
    python scripts/probar_ia.py G1 G2 S3     # solo esos casos (para afinar el prompt rápido)
"""
import copy
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para poder importar config, motor, ia y ui

import yaml

import config
from ia.explicar import _pedir_a_la_ia
from ia.reglas import fallas_graves, revisar
from ia.validador import cifras_inventadas
from motor.api import calcular_estado
from motor.datos import cargar
from ui.selector import perfil_demo

RUTA_CASOS = config.RAIZ / "scripts" / "combinaciones.yaml"
RUTA_SALIDA = config.RAIZ / "docs" / "textos_ia.json"

# Los 15 casos, en orden. G1 -> G2 -> G3 es el guion: cada uno se explica con el anterior.
# El resto se explica solo, como primera comparación. Se eligieron para cubrir todas las
# situaciones: señal clara, débil y no concluyente; grupo completado (E1, E3); una palanca
# bajada por debajo del valor real (E5); resto chico (R15-1) y las dos empresas de respaldo.
CASOS = ["G1", "G2", "G3", "S1", "S2", "S3", "S4", "D1", "D2", "E1", "E3", "E5", "R29-1", "R15-1", "R15-3"]
CADENA = {"G2": "G1", "G3": "G2"}  # caso -> su paso anterior

LIMITE_SEG = 15  # aquí no hay público esperando: más tiempo que en vivo
LIMITE_TOTAL_SEG = 30


def estado_de(caso, empresas, supuestos):
    """El estado real de un caso de combinaciones.yaml, tal como lo calcula la app."""
    perfil = perfil_demo(empresas, caso["empresa"])
    ultima = list(caso["palancas"])[-1]  # la última palanca del caso hace de "último clic"
    cambio = {"palanca": ultima, "de": perfil["palancas"].get(ultima), "a": caso["palancas"][ultima]}
    return calcular_estado(empresas, perfil, caso["palancas"], cambio, supuestos)


def probar(caso_id, estado, anterior, cliente=None):
    """Pide el texto a la IA y lo revisa. Nunca lanza error: un fallo queda anotado."""
    inicio = time.perf_counter()
    try:
        texto = _pedir_a_la_ia(
            copy.deepcopy(estado), anterior, cliente, LIMITE_SEG, LIMITE_TOTAL_SEG, None, config.MODELO_IA
        )
        error = None
    except Exception as e:  # noqa: BLE001  sin llave, sin internet, API caída...
        texto, error = "", f"{type(e).__name__}: {e}"
    return {
        "id": caso_id,
        "anterior": CADENA.get(caso_id),
        "segundos": round(time.perf_counter() - inicio, 2),
        "texto": texto,
        "error": error,
        "palabras": len(texto.split()),
        "cifras_inventadas": cifras_inventadas(texto, estado, anterior) if texto else [],
        "reglas_fallidas": revisar(texto, estado) if texto else ["sin texto"],
        "en_vivo": en_vivo(texto, estado, anterior),
        "estado": estado,  # se guarda para que la prueba pueda revisar el texto sin llamar a la IA
    }


def en_vivo(texto, estado, anterior):
    """Qué vería el jurado: "IA" si el texto pasa las mismas revisiones que ia/explicar.py, si no "plantilla".

    En vivo solo tumban un texto las cifras inventadas y las fallas graves (causa o advertencia
    faltante); el largo y la jerga no. Por eso un caso puede fallar aquí y aun así salir la IA.
    """
    if texto and not cifras_inventadas(texto, estado, anterior) and not fallas_graves(texto, estado):
        return "IA"
    return "plantilla"


def tabla_markdown(resultados):
    filas = [
        "| Caso | Palabras | Segundos | Cifras | Reglas | En vivo saldría |",
        "|---|---|---|---|---|---|",
    ]
    for r in resultados:
        cifras = "bien" if not r["cifras_inventadas"] else "inventa " + ", ".join(f"{x:g}" for x in r["cifras_inventadas"])
        reglas = "bien" if not r["reglas_fallidas"] else "; ".join(r["reglas_fallidas"])
        filas.append(f"| {r['id']} | {r['palabras']} | {r['segundos']} | {cifras} | {reglas} | {r['en_vivo']} |")
    textos = [f"### {r['id']}\n\n{r['texto'] or r['error']}\n" for r in resultados]
    return "\n".join(filas) + "\n\n" + "\n".join(textos)


def main(pedidos=None, cliente=None):
    empresas = cargar()
    supuestos = json.loads(config.RUTA_SUPUESTOS.read_text(encoding="utf-8"))
    casos = {c["id"]: c for c in yaml.safe_load(RUTA_CASOS.read_text(encoding="utf-8"))["casos"]}

    estados = {cid: estado_de(casos[cid], empresas, supuestos) for cid in CASOS}
    resultados = []
    for cid in pedidos or CASOS:
        anterior = estados.get(CADENA.get(cid))  # None si el caso no tiene paso anterior
        r = probar(cid, estados[cid], anterior, cliente)
        ok = not (r["cifras_inventadas"] or r["reglas_fallidas"])
        print(f"{cid:6} {r['segundos']:>5}s  {'OK   ' if ok else 'FALLA'}  en vivo: {r['en_vivo']}")
        resultados.append(r)

    if not pedidos:  # solo la corrida completa reescribe el archivo que lee la prueba
        RUTA_SALIDA.write_text(json.dumps(resultados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nGuardado en {RUTA_SALIDA.relative_to(config.RAIZ)}")

    bien = sum(1 for r in resultados if not (r["cifras_inventadas"] or r["reglas_fallidas"]))
    print(f"\n{bien} de {len(resultados)} cumplen todas las reglas\n")
    print(tabla_markdown(resultados))
    return 0 if bien == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
