"""Revisa data/processed/cache.json como lo vería el jurado. Dueño: Julian.

Para el día 12 del plan: "leer cada texto del caché y comprobar que los pasos del guion
responden al instante". Por cada paso de scripts/generar_cache.py:
  1. Calcula el estado con el motor real, igual que la app.
  2. Le pide la explicación a ia.explicar.explicar SIN internet (un cliente que siempre falla).
     Si el texto está en el caché, sale de ahí; si no, sale la plantilla.
  3. Mide cuánto tarda (sin el efecto de escritura) y revisa la forma con ia/reglas.py.
Escribe docs/revision_cache.md para leer los textos con calma.

Correr desde la raíz del repo (no gasta crédito: nunca llama a la IA):
    python scripts/revisar_cache.py
"""
import copy
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para poder importar config, motor, ia y ui

import json

import config
from ia.cache import cargar as cargar_cache
from ia.cache import llave
from ia.explicar import explicar
from ia.reglas import revisar
from motor.datos import cargar as cargar_empresas
from scripts.generar_cache import armar_secuencias, cargar_casos

RUTA_REPORTE = config.RAIZ / "docs" / "revision_cache.md"
LIMITE_GUION_SEG = 1.0  # "Listo cuando" del día 12: los pasos del guion salen en menos de 1 s


class SinInternet:
    """Un cliente de la API que siempre falla, como si el wifi del evento estuviera caído.

    Así la revisión dice la verdad: si un paso no está en el caché, se ve que sale la
    plantilla, en vez de que la IA lo escriba en el momento y lo esconda.
    """

    def __init__(self):
        self.messages = self

    def stream(self, **kwargs):
        raise ConnectionError("revisión sin internet")


def revisar_paso(estado, anterior, cache):
    """Lo que vería el jurado en un paso: de dónde sale el texto, cuánto tarda y qué reglas falla."""
    copia = copy.deepcopy(estado)  # explicar escribe en estado["explicacion"]; el original no se toca
    inicio = time.perf_counter()
    texto = "".join(explicar(copia, anterior, cliente=SinInternet(), cache=cache, pausa=0))
    segundos = time.perf_counter() - inicio
    clave = llave(estado, anterior)
    guardado = cache.get(clave) or cache.get(llave(estado)) or {}
    return {
        "llave": clave,
        "fuente": copia["explicacion"]["fuente"],
        "segundos": segundos,
        "creado": guardado.get("creado", "-"),
        "palabras": len(texto.split()),
        "fallas": revisar(texto, estado),
        "texto": texto,
    }


def revisar_todo(secuencias, cache):
    """Revisa cada paso en orden, con su anterior, sin repetir llaves. La primera secuencia es el guion."""
    filas, vistas = [], set()
    for numero, secuencia in enumerate(secuencias):
        anterior = None
        for estado in secuencia:
            clave = llave(estado, anterior)
            if clave not in vistas:
                vistas.add(clave)
                fila = revisar_paso(estado, anterior, cache)
                fila["guion"] = numero == 0
                filas.append(fila)
            anterior = estado
    sobrantes = sorted(set(cache) - vistas)  # llaves viejas que ningún paso usa
    return filas, sobrantes


def problemas(fila):
    """Lo que hay que arreglar en una fila (lista vacía = bien)."""
    lista = []
    if fila["fuente"] != "cache":
        lista.append(f"sale de la {fila['fuente']}, no del caché")
    if fila["guion"] and fila["segundos"] > LIMITE_GUION_SEG:
        lista.append(f"tarda {fila['segundos']:.2f} s (máximo {LIMITE_GUION_SEG:g} s en el guion)")
    return lista + fila["fallas"]


def a_markdown(filas, sobrantes):
    bien = sum(1 for f in filas if not problemas(f))
    lineas = [
        "# Revisión del caché",
        "",
        "Generado por `scripts/revisar_cache.py`, sin internet. Dueño: Julian.",
        "",
        f"**{bien} de {len(filas)} pasos sin problemas.**",
        "",
        "| # | Guion | Fuente | Segundos | Palabras | Creado | Problemas |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, f in enumerate(filas, 1):
        detalle = "; ".join(problemas(f)) or "bien"
        lineas.append(
            f"| {i} | {'sí' if f['guion'] else ''} | {f['fuente']} | {f['segundos']:.3f} | "
            f"{f['palabras']} | {f['creado']} | {detalle} |"
        )
    lineas += ["", "## Textos", ""]
    for i, f in enumerate(filas, 1):
        lineas += [f"### {i}. `{f['llave']}`", "", f["texto"], ""]
    if sobrantes:
        lineas += ["## Llaves del caché que ningún paso usa", ""]
        lineas += [f"- `{s}`" for s in sobrantes]
        lineas.append("")
    return "\n".join(lineas)


def main(cache=None):
    cache = cargar_cache() if cache is None else cache
    supuestos = json.loads(config.RUTA_SUPUESTOS.read_text(encoding="utf-8"))
    secuencias = armar_secuencias(cargar_casos(), cargar_empresas(), supuestos)
    filas, sobrantes = revisar_todo(secuencias, cache)

    for i, f in enumerate(filas, 1):
        lista = problemas(f)
        marca = "OK   " if not lista else "REVISA"
        print(f"{i:>2} {marca} {f['fuente']:9} {f['segundos']:.3f}s  {f['llave']}")
        for p in lista:
            print(f"        - {p}")
    RUTA_REPORTE.write_text(a_markdown(filas, sobrantes), encoding="utf-8")
    bien = sum(1 for f in filas if not problemas(f))
    print(f"\n{bien} de {len(filas)} pasos sin problemas. Textos completos en docs/{RUTA_REPORTE.name}")
    return 0 if bien == len(filas) else 1


if __name__ == "__main__":
    sys.exit(main())
