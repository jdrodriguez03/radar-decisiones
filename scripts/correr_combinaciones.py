
"""Corre las 20 combinaciones y escribe docs/resultados_combinaciones.md. Dueño: Juanes.

Para qué sirve: antes de la demo queremos saber qué pasa en las 20 jugadas más
probables (las del guion, cada palanca sola, extremos y empresas de respaldo).
Así sabemos de antemano si alguna da un resultado raro que un juez pueda provocar.

Cómo se corre (desde la raíz del repositorio):
    python scripts/correr_combinaciones.py
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import yaml

# Para poder importar config y motor aunque el script viva dentro de scripts/
RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from config import MIN_GRUPO, PALANCAS, RUTA_SUPUESTOS
from motor.comparar import comparar
from motor.pesos import costo_brecha, costo_medida

RUTA_CASOS = RAIZ / "scripts" / "combinaciones.yaml"
RUTA_SALIDA = RAIZ / "docs" / "resultados_combinaciones.md"


# ---------------------------------------------------------------------------
# 1. Leer los casos y los supuestos
# ---------------------------------------------------------------------------
def cargar_casos(ruta=RUTA_CASOS):
    """Lee combinaciones.yaml y revisa que cada caso esté bien escrito."""
    with open(ruta, encoding="utf-8") as f:
        casos = yaml.safe_load(f)["casos"]
    for caso in casos:
        validar_caso(caso)
    return casos


def validar_caso(caso):
    """Lanza un error claro si un caso tiene una palanca mal escrita o fuera de rango."""
    for campo in ("id", "empresa", "palancas"):
        if campo not in caso:
            raise ValueError(f"Al caso {caso.get('id', '?')} le falta el campo '{campo}'.")
    for palanca, valor in caso["palancas"].items():
        if palanca not in PALANCAS:
            raise ValueError(f"Caso {caso['id']}: la palanca '{palanca}' no existe.")
        minimo, maximo, _paso = PALANCAS[palanca]
        if not minimo <= valor <= maximo:
            raise ValueError(
                f"Caso {caso['id']}: {palanca}={valor} está fuera del rango {minimo} a {maximo}."
            )


def cargar_supuestos(ruta=RUTA_SUPUESTOS):
    """Lee el costo por baja y el costo mensual por ruta de supuestos.json."""
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# 2. Datos de la empresa elegida
# ---------------------------------------------------------------------------
def fila_empresa(empresas, empresa_id):
    """Devuelve la fila de una empresa, tenga el DataFrame la empresa como índice o columna."""
    if "empresa" in empresas.columns:
        filas = empresas[empresas["empresa"] == empresa_id]
        if filas.empty:
            raise ValueError(f"No existe la empresa {empresa_id}.")
        return filas.iloc[0]
    return empresas.loc[empresa_id]


def perfil_de(fila):
    """Arma el perfil que necesita pesos.py: plantilla y valores actuales de las palancas."""
    return {
        "plantilla_op": float(fila["plantilla_op"]),
        "palancas": {palanca: float(fila[palanca]) for palanca in PALANCAS},
    }


# ---------------------------------------------------------------------------
# 3. Leer la salida del motor sin depender de su forma exacta
# ---------------------------------------------------------------------------
def rotacion(resumen):
    """Rotación anual (mediana) de un resumen del motor.

    Acepta las dos formas posibles: {"rot_anual": x} o {"indicadores": {"rot_anual": x}}.
    """
    if "indicadores" in resumen:
        return resumen["indicadores"].get("rot_anual")
    return resumen.get("rot_anual")


def etiqueta_senal(senal):
    """La señal puede venir como texto ("clara") o como dict {"etiqueta": ..., "p": ...}."""
    return senal["etiqueta"] if isinstance(senal, dict) else senal


# ---------------------------------------------------------------------------
# 4. Correr un caso
# ---------------------------------------------------------------------------
def correr_caso(empresas, caso, supuestos):
    """Llama al motor y a los pesos para un caso y devuelve una fila con los resultados."""
    fila = fila_empresa(empresas, caso["empresa"])
    perfil = perfil_de(fila)
    movidas = caso["palancas"]

    resultado = comparar(empresas, caso["empresa"], movidas)
    grupo, resto = resultado["grupo"], resultado["resto"]
    rot_empresa = float(fila["rot_anual"])
    rot_grupo, rot_resto = rotacion(grupo), rotacion(resto)

    medida = costo_medida(perfil, movidas, supuestos)
    brecha = (
        costo_brecha(rot_empresa, rot_grupo, perfil["plantilla_op"], supuestos["costo_por_baja"])
        if rot_grupo is not None
        else 0.0
    )

    salida = {
        "id": caso["id"],
        "tipo": caso.get("tipo", ""),
        "descripcion": caso.get("descripcion", ""),
        "empresa": caso["empresa"],
        "palancas": movidas,
        "n_grupo": grupo["n"],
        "n_resto": resto["n"],
        "rot_empresa": rot_empresa,
        "rot_grupo": rot_grupo,
        "rot_resto": rot_resto,
        "senal": etiqueta_senal(resultado["senal"]),
        "completado": bool(resultado.get("completado", False)),
        "costo_medida": medida,
        "costo_brecha": brecha,
    }
    salida["alertas"] = alertas(salida)
    salida["revision_guion"] = revisar_esperado(salida, caso.get("esperado"))
    return salida


def alertas(fila):
    """Las tres alertas que pide la guía: grupo vacío, resto chico y grupo que rota más."""
    lista = []
    if fila["n_grupo"] == 0:
        lista.append("grupo vacío")
    if fila["n_resto"] < MIN_GRUPO:
        lista.append(f"resto con menos de {MIN_GRUPO}")
    if (
        fila["rot_grupo"] is not None
        and fila["rot_resto"] is not None
        and fila["rot_grupo"] > fila["rot_resto"]
    ):
        lista.append("el grupo rota más que el resto")
    return lista


def revisar_esperado(fila, esperado):
    """Si el caso trae cifras esperadas (pasos del guion), dice si el motor las reproduce."""
    if not esperado:
        return ""
    fallas = []
    if fila["n_grupo"] != esperado["n_grupo"]:
        fallas.append(f"n grupo {fila['n_grupo']} ≠ {esperado['n_grupo']}")
    for clave in ("rot_grupo", "rot_resto"):
        if round(fila[clave], 2) != esperado[clave]:
            fallas.append(f"{clave} {fila[clave]:.3f} ≠ {esperado[clave]}")
    return "coincide" if not fallas else "NO coincide: " + "; ".join(fallas)


# ---------------------------------------------------------------------------
# 5. Formato y archivo de salida
# ---------------------------------------------------------------------------
def pct(valor):
    return "—" if valor is None else f"{valor:.0%}"


def pesos(valor):
    """6341580 -> $6.3 M ; 650000 -> $650 mil ; negativos con signo."""
    signo = "−" if valor < 0 else ""
    valor = abs(valor)
    if valor >= 1_000_000:
        return f"{signo}${valor / 1_000_000:.1f} M"
    if valor >= 1_000:
        return f"{signo}${valor / 1_000:.0f} mil"
    return f"{signo}${valor:.0f}"


def texto_palancas(palancas):
    return ", ".join(f"{k}={v}" for k, v in palancas.items())


def a_markdown(filas, supuestos):
    con_alerta = [f for f in filas if f["alertas"]]
    guion = [f for f in filas if f["revision_guion"]]
    lineas = [
        "# Resultados de las 20 combinaciones",
        "",
        f"Generado por scripts/correr_combinaciones.py el {date.today().isoformat()}. "
        f"Costo por baja: ${supuestos['costo_por_baja']:,}; "
        f"costo mensual por ruta: ${supuestos['costo_ruta_mensual']:,}.",
        "",
        f"**Resumen:** {len(filas)} casos corridos, {len(con_alerta)} con alerta, "
        f"{sum(f['completado'] for f in filas)} con grupo completado.",
        "",
        "## Tabla",
        "",
        "| Caso | Empresa | Palancas movidas | n grupo | n resto | Rot. empresa | Rot. grupo "
        "| Rot. resto | Señal | Completado | Costo medida | Costo brecha | Alertas |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for f in filas:
        lineas.append(
            f"| {f['id']} | {f['empresa']} | {texto_palancas(f['palancas'])} "
            f"| {f['n_grupo']} | {f['n_resto']} | {pct(f['rot_empresa'])} "
            f"| {pct(f['rot_grupo'])} | {pct(f['rot_resto'])} | {f['senal']} "
            f"| {'sí' if f['completado'] else 'no'} | {pesos(f['costo_medida'])} "
            f"| {pesos(f['costo_brecha'])} | {'; '.join(f['alertas']) or '—'} |"
        )

    lineas += ["", "## Revisión de los pasos del guion", ""]
    for f in guion:
        lineas.append(f"- **{f['id']}** ({f['descripcion']}): {f['revision_guion']}")

    lineas += ["", "## Casos con alerta", ""]
    if not con_alerta:
        lineas.append("Ninguno.")
    for f in con_alerta:
        lineas.append(
            f"- **{f['id']}** · {f['descripcion']}: {', '.join(f['alertas'])} "
            f"(grupo {pct(f['rot_grupo'])} contra resto {pct(f['rot_resto'])}, "
            f"n = {f['n_grupo']} vs {f['n_resto']})."
        )
    return "\n".join(lineas) + "\n"


def correr(empresas, casos, supuestos):
    """Corre todos los casos y devuelve la lista de filas (útil para pruebas)."""
    return [correr_caso(empresas, caso, supuestos) for caso in casos]


def main(empresas=None):
    if empresas is None:
        from motor.datos import cargar

        empresas = cargar()
    casos = cargar_casos()
    supuestos = cargar_supuestos()
    filas = correr(empresas, casos, supuestos)
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    RUTA_SALIDA.write_text(a_markdown(filas, supuestos), encoding="utf-8")
    print(f"Listo: {len(filas)} casos -> {RUTA_SALIDA}")
    print(f"Con alerta: {sum(bool(f['alertas']) for f in filas)}")


if __name__ == "__main__":
    main()