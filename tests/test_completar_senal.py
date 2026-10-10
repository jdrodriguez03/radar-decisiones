import pytest

from motor.comparar import comparar
from motor.datos import cargar


@pytest.fixture(scope="module")
def empresas():
    return cargar()

# test para verificar que la función comparar devuelve el grupo
def test_prima_50_por_ciento_da_grupo_16_y_senal_debil(empresas):
    resultado = comparar(
        empresas,
        "COMPAÑIA 36",
        {"aguinaldo_op": 20, "prima_vac_op": 0.5},
    )

    assert resultado["grupo"]["n"] == 16
    assert resultado["resto"]["n"] == 22
    assert resultado["senal"]["etiqueta"] == "débil"
    assert resultado["senal"]["p"] == pytest.approx(0.051, abs=0.005)

# test para verificar que la función comparar completa el grupo con empresas similares si el grupo inicial es menor que el tamaño mínimo.
def test_tamano_parecido_completa_el_grupo_a_cinco(empresas):
    resultado = comparar(
        empresas,
        "COMPAÑIA 36",
        {"aguinaldo_op": 20, "prima_vac_op": 0.5, "sal_dia_ini": 350},
        solo_tamano=True,
    )

    assert resultado["grupo"]["n"] == 5
    assert resultado["completado"] is True
    assert resultado["senal"]["etiqueta"] == "no concluyente"

# test para verificar que la función comparar no marca completado si el grupo inicial es mayor o igual al tamaño mínimo.
def test_salario_350_sin_filtro_de_tamano_no_marca_completado(empresas):
    resultado = comparar(
        empresas,
        "COMPAÑIA 36",
        {"aguinaldo_op": 20, "prima_vac_op": 0.5, "sal_dia_ini": 350},
    )

    assert resultado["grupo"]["n"] == 5
    assert resultado["completado"] is False
    assert resultado["senal"]["etiqueta"] == "no concluyente"
