"""Guardado y comparación de escenarios A y B. Dueño: Aleja."""
from copy import deepcopy
from numbers import Real

import streamlit as st
# Se crea clave para guardar los escenarios en session_state
CLAVE_ESCENARIOS = "escenarios_ab"
# se definen funciones para mostrar los escenarios guardados y sus diferencias

def guardar(estado: dict) -> dict:
    """Guarda una copia completa del estado como A o B en la sesión actual."""
    if not isinstance(estado, dict):
        raise TypeError("estado debe ser un diccionario.")
# se validan los campos requeridos en el estado
    empresa = estado.get("empresa")
    palancas_movidas = estado.get("palancas_movidas")
    pesos = estado.get("pesos")
    if not isinstance(empresa, dict) or not isinstance(palancas_movidas, dict):
        raise TypeError("estado debe incluir empresa y palancas_movidas como diccionarios.")
    if not isinstance(pesos, dict) or not isinstance(pesos.get("supuestos"), dict):
        raise TypeError("estado debe incluir los supuestos dentro de pesos como diccionario.")
# se valida que no haya más de dos escenarios guardados
    escenarios = st.session_state.get(CLAVE_ESCENARIOS, [])
    if not isinstance(escenarios, list):
        raise TypeError("Los escenarios guardados deben ser una lista.")
    if len(escenarios) >= 2:
        raise ValueError("Ya hay dos escenarios guardados; limpia la comparación para empezar otra.")
# se guarda el escenario actual como A o B según corresponda con copia de los campos requeridos
    copia = deepcopy(estado)
    escenario = {
        "nombre": "A" if not escenarios else "B",
        "empresa": deepcopy(copia["empresa"]),
        "palancas_movidas": deepcopy(copia["palancas_movidas"]),
        "supuestos": deepcopy(copia["pesos"]["supuestos"]),
        "estado": copia,
    }
    st.session_state[CLAVE_ESCENARIOS] = [*escenarios, escenario]
    return deepcopy(escenario)
# se crea valor_numerico para validar que los valores sean numéricos o None.

def _valor_numerico(valor: object, nombre: str) -> Real | None:
    if valor is None:
        return None
    if not isinstance(valor, Real) or isinstance(valor, bool):
        raise TypeError(f"{nombre} debe ser numérico o None.")
    return valor
# se crea diferencia para calcular la diferencia B − A, devolviendo None si alguno de los dos es None.

def _diferencia(a: Real | None, b: Real | None) -> float | int | None:
    return None if a is None or b is None else b - a
# se crea comparar_numeros para comparar dos valores numéricos y devolver un diccionario con la diferencia y cuál es mayor o menor.

def _comparar_numeros(a: Real | None, b: Real | None) -> dict:
    diferencia = _diferencia(a, b)
    if a is None or b is None or a == b:
        mayor = menor = "empate" if a == b else None
    else:
        mayor = "A" if a > b else "B"
        menor = "A" if a < b else "B"
    return {
        "a": a,
        "b": b,
        "diferencia_b_menos_a": diferencia,
        "mayor": mayor,
        "menor": menor,
    }
# se crea función para extraer las métricas de un estado completo y validar que contenga los campos requeridos.

def _metricas(estado: dict, nombre: str) -> dict:
    if not isinstance(estado, dict):
        raise TypeError(f"El escenario {nombre} debe ser un diccionario.")

    try:
        grupo = estado["grupo"]
        indicadores = grupo["indicadores"]
        senal = estado["senal"]
        pesos = estado["pesos"]
        n_grupo = grupo["n"]
        rotacion = indicadores["rot_anual"]
        costo_medida = pesos["costo_medida_anual"]
        costo_brecha = pesos["costo_brecha_anual"]
    except (KeyError, TypeError) as error:
        raise ValueError(
            f"El escenario {nombre} no contiene grupo, indicadores, señal y pesos completos."
        ) from error

    if not isinstance(senal, dict):
        raise TypeError(f"La señal del escenario {nombre} debe ser un diccionario.")
    return {
        "n_grupo": _valor_numerico(n_grupo, f"n del grupo de {nombre}"),
        "rotacion_grupo": _valor_numerico(rotacion, f"rotación del grupo de {nombre}"),
        "senal": deepcopy(senal),
        "costo_medida": _valor_numerico(costo_medida, f"costo de medida de {nombre}"),
        "costo_brecha": _valor_numerico(costo_brecha, f"costo de brecha de {nombre}"),
    }
# se crea función para comparar dos estados completos y devolver un diccionario con las diferencias B − A.

def comparar_escenarios(a: dict, b: dict) -> dict:
    """Compara dos estados completos y expresa las diferencias como B menos A."""
    metricas_a = _metricas(a, "A")
    metricas_b = _metricas(b, "B")
    senal_a = metricas_a["senal"]
    senal_b = metricas_b["senal"]

    return {
        "n_grupo": _comparar_numeros(metricas_a["n_grupo"], metricas_b["n_grupo"]),
        "rotacion_grupo": _comparar_numeros(
            metricas_a["rotacion_grupo"], metricas_b["rotacion_grupo"]
        ),
        "senal": {
            "a": senal_a,
            "b": senal_b,
            "cambio": senal_a.get("etiqueta") != senal_b.get("etiqueta"),
        },
        "costo_medida": _comparar_numeros(
            metricas_a["costo_medida"], metricas_b["costo_medida"]
        ),
        "costo_brecha": _comparar_numeros(
            metricas_a["costo_brecha"], metricas_b["costo_brecha"]
        ),
    }
