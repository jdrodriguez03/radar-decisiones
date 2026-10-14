"""Caché de explicaciones precalculadas: llave, lectura, búsqueda y escritura. Dueño: Julian.

data/processed/cache.json guarda textos ya generados por la IA para los pasos del guion.
En la demo, si el estado está en el caché, la explicación sale al instante y sin internet.

Formato del archivo:
    {"COMPAÑIA 36|aguinaldo_op=20|15000": {"texto": "...", "modelo": "...", "creado": "2026-10-11"}, ...}
"""
import json

import config
from ia.prompts import anterior_util
from ia.validador import es_valido


def _num(valor):
    """20, 20.0 y 20.00 son la misma palanca: se escriben igual en la llave."""
    return f"{float(valor):g}"


def _firma(estado):
    """'COMPAÑIA 36|aguinaldo_op=20,prima_vac_op=0.5|15000': empresa, palancas movidas y costo por baja."""
    empresa = estado["empresa"]["id"]
    movidas = estado.get("palancas_movidas") or {}
    palancas = ",".join(f"{p}={_num(v)}" for p, v in sorted(movidas.items())) or "sin cambios"
    costo = _num(estado["pesos"]["supuestos"]["costo_por_baja"])
    return f"{empresa}|{palancas}|{costo}"


def llave(estado, anterior=None):
    """La llave del caché.

    El texto depende del paso anterior ("quedan 16 empresas, antes 22"), así que si el
    anterior cuenta (misma regla que armar_mensaje), su firma va en la llave después de "<-".
    """
    previo = anterior_util(estado, anterior)
    if previo is None:
        return _firma(estado)
    return f"{_firma(estado)} <- {_firma(previo)}"


def cargar(ruta=None):
    """Lee el caché. Si no existe o está dañado, devuelve {}: un caché roto nunca tumba la demo."""
    ruta = ruta or config.RUTA_CACHE
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def guardar(cache, ruta=None):
    """Escribe el caché ordenado por llave, legible y con acentos (para revisarlo a mano el día 12)."""
    ruta = ruta or config.RUTA_CACHE
    ruta.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def buscar(estado, anterior=None, cache=None):
    """El texto guardado para este estado, o None.

    Primero busca la llave exacta (con el paso anterior). Si no está, busca la del estado
    solo: un texto sin "antes..." es correcto venga de donde venga el usuario.
    Todo texto pasa por el validador antes de devolverse: si el motor cambió una cifra
    después de generar el caché, o alguien editó el texto a mano y se equivocó, se descarta.
    """
    cache = cargar() if cache is None else cache
    try:
        intentos = ((llave(estado, anterior), anterior), (llave(estado), None))
    except (KeyError, TypeError):  # estado incompleto (sin pesos, sin empresa): no hay llave posible
        return None
    for clave, previo in intentos:
        guardado = cache.get(clave)
        if guardado and es_valido(guardado["texto"], estado, previo):
            return guardado["texto"]
    return None
