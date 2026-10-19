"""Genera las explicaciones precalculadas del guion. Dueño: Julian."""
import copy
from datetime import UTC, datetime

import config
from ia.cache import cargar, guardar, llave
from ia.explicar import explicar
from ia.validador import es_valido

LIMITE_PRECALCULO_SEG = 15  # aquí no hay público esperando: se le da más tiempo a la IA que en vivo
LIMITE_TOTAL_PRECALCULO_SEG = 30


def precalcular(estados, cliente=None, ruta=None, rehacer=False):
    """Explica cada estado con la IA y guarda los textos válidos en el caché.

    `estados` va en el orden en que se recorren en la demo: cada uno se explica con el
    anterior de la lista como paso anterior (si es de la misma empresa y ya tenía una
    palanca movida, igual que en la app). Así el texto del paso 02 dice "antes 22".

    Solo se guardan textos de la IA que pasaron el validador (fuente "llm"): si la IA
    falla o inventa una cifra, ese estado queda fuera y en vivo saldrá la plantilla.
    Con rehacer=False no se vuelven a pedir los que ya están (ahorra tiempo y crédito),
    salvo los que ya no pasan el validador: si el motor cambió una cifra después de
    generarlos, en vivo saldría la plantilla, así que se piden de nuevo. Un texto editado
    a mano que sigue siendo válido se conserva.

    Devuelve un resumen: {"guardadas": [...], "ya_estaban": [...], "fallidas": [...]}.
    """
    cache = cargar(ruta)
    resumen = {"guardadas": [], "ya_estaban": [], "fallidas": []}
    anterior = None
    for estado in estados:
        clave = llave(estado, anterior)
        guardado = cache.get(clave)
        vigente = guardado is not None and es_valido(guardado["texto"], estado, anterior)
        if vigente and not rehacer:
            resumen["ya_estaban"].append(clave)
        else:
            copia = copy.deepcopy(estado)  # explicar escribe en estado["explicacion"]; el original no se toca
            pedido = explicar(
                copia, anterior, cliente=cliente, cache={},
                limite=LIMITE_PRECALCULO_SEG, limite_total=LIMITE_TOTAL_PRECALCULO_SEG, pausa=0,
            )
            for _ in pedido:
                pass  # se consume el generador completo, como lo haría la pantalla
            if copia["explicacion"]["fuente"] == "llm":
                cache[clave] = {
                    "texto": copia["explicacion"]["texto"],
                    "modelo": config.MODELO_IA,
                    "creado": datetime.now(UTC).date().isoformat(),
                }
                resumen["guardadas"].append(clave)
            else:
                cache.pop(clave, None)  # un texto vencido no se deja: en vivo saldría la plantilla igual
                resumen["fallidas"].append(clave)
        anterior = estado
    guardar(cache, ruta)
    return resumen
