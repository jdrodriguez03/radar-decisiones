import pandas as pd
import pytest

from motor.comparar import comparar, completar_con_similares
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


def test_e1_conserva_empresas_del_grupo_y_agrega_solo_las_faltantes(empresas):
    empresa = next(
        empresa for empresa in empresas["empresa"].astype(str)
        if empresa.endswith("36")
    )
    universo = empresas.loc[empresas["empresa"].ne(empresa)]
    iniciales = universo.loc[universo["sal_dia_ini"].ge(380), "empresa"].astype(str)
    resultado = comparar(empresas, empresa, {"sal_dia_ini": 380})

    ids_grupo = set(resultado["grupo"]["ids"])
    ids_resto = set(resultado["resto"]["ids"])
    ids_universo = set(universo["empresa"].astype(str))

    assert len(iniciales) == 2
    assert resultado["completado"] is True
    assert len(ids_grupo) == 5
    assert set(iniciales).issubset(ids_grupo)
    assert len(ids_grupo - set(iniciales)) == 3
    assert ids_grupo.isdisjoint(ids_resto)
    assert ids_grupo | ids_resto == ids_universo


def test_similares_resuelve_empates_por_id_de_forma_estable():
    universo = pd.DataFrame(
        {
            "empresa": ["Z", "A"],
            "aguinaldo_op": [15.0, 25.0],
        }
    )

    resultado = completar_con_similares(
        universo,
        {"aguinaldo_op": 20.0},
        k=1,
    )

    assert resultado["empresa"].tolist() == ["A"]
