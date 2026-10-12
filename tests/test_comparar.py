import pytest

from motor.comparar import comparar, resumen, senal
from motor.datos import cargar

 
@pytest.fixture(scope="module")
def empresas():
    return cargar()

# test para verificar que la función comparar devuelve el grupo
#  y resto correctos para una empresa específica y un conjunto de palancas movidas.
def test_aguinaldo_20_reproduce_grupo_y_resto_del_guion(empresas):
    resultado = comparar(empresas, "COMPAÑIA 36", {"aguinaldo_op": 20})

    assert resultado["grupo"]["n"] == 22
    assert resultado["resto"]["n"] == 16
    assert resultado["grupo"]["indicadores"]["rot_anual"] == pytest.approx(0.222)
    assert resultado["resto"]["indicadores"]["rot_anual"] == pytest.approx(0.534)
    assert resultado["completado"] is False

# test para verificar que la función comparar completa el grupo con empresas similares si el grupo inicial es menor que el tamaño mínimo.
def test_resumen_usa_los_nombres_del_contrato(empresas):
    grupo = empresas.loc[empresas["empresa"].isin(["COMPAÑIA 2", "COMPAÑIA 3"])]

    resultado = resumen(grupo)

    assert resultado["n"] == 2
    assert resultado["ids"] == ["COMPAÑIA 2", "COMPAÑIA 3"]
    assert set(resultado["indicadores"]) == {"rot_anual", "rot_temprana", "ausentismo"}

# test para verificar que la función senal devuelve "no aplica" si el resto está vacío.
def test_senal_es_no_aplica_si_el_resto_esta_vacio(empresas):
    grupo = empresas.loc[empresas["empresa"].ne("COMPAÑIA 36")]
    resto = empresas.iloc[0:0]

    assert senal(grupo, resto) == {"etiqueta": "no aplica", "p": None}

# se prueba que la función comparar con el parámetro solo_tamano=True filtra 
# correctamente las empresas para que el grupo y el resto tengan tamaños similares.
def test_comparar_solo_tamano_filtra_la_misma_banda(empresas):
    resultado = comparar(
        empresas,
        "COMPAÑIA 36",
        {"aguinaldo_op": 20},
        solo_tamano=True,
    )

    assert resultado["grupo"]["n"] + resultado["resto"]["n"] == 12
