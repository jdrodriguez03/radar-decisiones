import json

import pytest

from config import RUTA_EJEMPLO, RUTA_SUPUESTOS
from contrato.modelo import validar
from motor.api import calcular_estado
from motor.datos import cargar
from ui.selector import perfil_demo


# test para verificar que la función calcular_estado devuelve un estado que coincide con un ejemplo predefinido, 
# incluyendo la validación del estado y la comparación de los resultados con los valores esperados.
def test_calcular_estado_aguinaldo_coincide_con_el_ejemplo():
    empresas = cargar()
    perfil = perfil_demo(empresas, "COMPAÑIA 36")
    ejemplo = json.loads(RUTA_EJEMPLO.read_text(encoding="utf-8"))
    supuestos = json.loads(RUTA_SUPUESTOS.read_text(encoding="utf-8"))

    estado = calcular_estado(
        empresas,
        perfil,
        {"aguinaldo_op": 20.0},
        {"palanca": "aguinaldo_op", "de": 15.0, "a": 20.0},
        supuestos,
    )

    validar(estado)
    assert estado["empresa"]["id"] == ejemplo["empresa"]["id"]
    assert estado["empresa"]["plantilla_op"] == ejemplo["empresa"]["plantilla_op"]
    assert estado["empresa"]["palancas"] == pytest.approx(
        ejemplo["empresa"]["palancas"], abs=0.01
    )
    assert estado["empresa"]["indicadores"] == pytest.approx(
        ejemplo["empresa"]["indicadores"]
    )
    assert estado["cambio"] == ejemplo["cambio"]
    assert estado["palancas_movidas"] == ejemplo["palancas_movidas"]
    for nombre_grupo in ("grupo", "resto"):
        obtenido = estado[nombre_grupo]
        esperado = ejemplo[nombre_grupo]
        assert obtenido["n"] == esperado["n"]
        assert obtenido["indicadores"] == pytest.approx(esperado["indicadores"])
        assert len(obtenido["ids"]) == obtenido["n"]
    assert estado["grupo"]["completado"] == ejemplo["grupo"]["completado"]
    assert estado["senal"]["etiqueta"] == ejemplo["senal"]["etiqueta"]
    assert estado["senal"]["p"] == pytest.approx(ejemplo["senal"]["p"], abs=0.001)
    assert estado["en_comun"][0] == ejemplo["en_comun"][0]
    assert estado["pesos"]["costo_medida_anual"] == pytest.approx(
        ejemplo["pesos"]["costo_medida_anual"], abs=1
    )
    assert estado["pesos"]["costo_brecha_anual"] == pytest.approx(
        ejemplo["pesos"]["costo_brecha_anual"], abs=1
    )
    assert estado["explicacion"] is None

# test para verificar que la función calcular_estado maneja correctamente el caso en el que el resto está vacío.
def test_calcular_estado_inicial_cumple_el_contrato():
    empresas = cargar()
    perfil = perfil_demo(empresas, "COMPAÑIA 36")
    supuestos = json.loads(RUTA_SUPUESTOS.read_text(encoding="utf-8"))

    estado = calcular_estado(empresas, perfil, {}, None, supuestos)

    validar(estado)
    assert estado["cambio"] is None
    assert estado["palancas_movidas"] == {}
    assert estado["grupo"]["n"] == 39
    assert estado["resto"]["n"] == 0
    assert estado["resto"]["indicadores"] is None
