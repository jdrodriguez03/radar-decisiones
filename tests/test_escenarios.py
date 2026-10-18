"""Pruebas de los escenarios A y B con estados reales del motor."""
import copy
import json

import pytest
from streamlit.testing.v1 import AppTest

from config import RUTA_SUPUESTOS
from motor.api import calcular_estado
from motor.datos import cargar
from ui.escenarios import CLAVE_ESCENARIOS, comparar_escenarios
from ui.selector import perfil_demo
# se crean fixtures para cargar estados reales de la compañía 36 y se crean pruebas para comparar escenarios y guardar copias independientes de los estados.

@pytest.fixture(scope="module")
def estados_reales():
    empresas = cargar()
    perfil = perfil_demo(empresas, "COMPAÑIA 36")
    with RUTA_SUPUESTOS.open(encoding="utf-8") as archivo:
        supuestos = json.load(archivo)
# se calculan dos estados reales con diferentes palancas movidas para la compañía 36
    estado_a = calcular_estado(
        empresas,
        perfil,
        {"aguinaldo_op": 20},
        {"palanca": "aguinaldo_op", "de": 15, "a": 20},
        supuestos,
    )
    estado_b = calcular_estado(
        empresas,
        perfil,
        {"aguinaldo_op": 20, "prima_vac_op": 0.5},
        {"palanca": "prima_vac_op", "de": 0.25, "a": 0.5},
        supuestos,
    )
    return estado_a, estado_b
# se crean pruebas para comparar escenarios y guardar copias independientes de los estados.

def test_comparar_escenarios_calcula_diferencias_de_dos_estados_reales(estados_reales):
    estado_a, estado_b = estados_reales

    diferencias = comparar_escenarios(estado_a, estado_b)

    assert diferencias["n_grupo"]["a"] == 22
    assert diferencias["n_grupo"]["b"] == 16
    assert diferencias["n_grupo"]["diferencia_b_menos_a"] == -6
    assert diferencias["n_grupo"]["mayor"] == "A"
    assert diferencias["rotacion_grupo"]["a"] == pytest.approx(0.222)
    assert diferencias["rotacion_grupo"]["b"] == pytest.approx(0.174)
    assert diferencias["rotacion_grupo"]["diferencia_b_menos_a"] == pytest.approx(-0.048)
    assert diferencias["senal"]["a"] == estado_a["senal"]
    assert diferencias["senal"]["b"] == estado_b["senal"]
    assert diferencias["senal"]["cambio"] is True
    assert diferencias["costo_medida"]["a"] == estado_a["pesos"]["costo_medida_anual"]
    assert diferencias["costo_medida"]["b"] == estado_b["pesos"]["costo_medida_anual"]
    assert diferencias["costo_brecha"]["a"] == estado_a["pesos"]["costo_brecha_anual"]
    assert diferencias["costo_brecha"]["b"] == estado_b["pesos"]["costo_brecha_anual"]
    assert diferencias["costo_medida"]["menor"] == (
        "A"
        if estado_a["pesos"]["costo_medida_anual"]
        < estado_b["pesos"]["costo_medida_anual"]
        else "B"
    )
    assert diferencias["costo_brecha"]["menor"] == (
        "A"
        if estado_a["pesos"]["costo_brecha_anual"]
        < estado_b["pesos"]["costo_brecha_anual"]
        else "B"
    )
# se crea prueba para verificar que la señal solo cambia si cambia su etiqueta

def test_senal_solo_cambia_si_cambia_la_etiqueta(estados_reales):
    estado_a = copy.deepcopy(estados_reales[0])
    estado_b = copy.deepcopy(estado_a)
    estado_b["senal"]["p"] = 0.5

    diferencias = comparar_escenarios(estado_a, estado_b)

    assert diferencias["senal"]["cambio"] is False
# se crea función para guardar dos escenarios y verificar que se conserven copias independientes y que se rechace un tercer escenario.

def _guardar_dos(estado_a, estado_b):
    import streamlit as st

    from ui.escenarios import guardar

    guardar(estado_a)
    estado_a["grupo"]["n"] = -1
    guardar(estado_b)
    st.session_state["error_tercero"] = ""
    try:
        guardar(estado_a)
    except ValueError as error:
        st.session_state["error_tercero"] = str(error)
# se crea prueba para verificar que se conserven copias independientes de los escenarios guardados y que se rechace un tercer escenario.

def test_guardar_conserva_dos_copias_independientes_y_rechaza_un_tercero(estados_reales):
    estado_a, estado_b = copy.deepcopy(estados_reales)

    app = AppTest.from_function(_guardar_dos, args=(estado_a, estado_b)).run()

    assert not app.exception
    guardados = app.session_state[CLAVE_ESCENARIOS]
    assert [escenario["nombre"] for escenario in guardados] == ["A", "B"]
    assert guardados[0]["estado"]["grupo"]["n"] == 22
    assert guardados[1]["estado"]["grupo"]["n"] == 16
    assert guardados[0]["empresa"] == estado_a["empresa"]
    assert guardados[0]["palancas_movidas"] == estado_a["palancas_movidas"]
    assert guardados[0]["supuestos"] == estado_a["pesos"]["supuestos"]
    assert "Ya hay dos escenarios guardados" in app.session_state["error_tercero"]
