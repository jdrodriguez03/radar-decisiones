import pandas as pd
import pytest

from motor.comparar import comparar
from motor.datos import cargar
from motor.en_comun import diferencias_principales


# Se define un fixture de pytest llamado "empresas" que carga los datos de las 
# empresas desde la función cargar() del módulo motor.datos.
@pytest.fixture(scope="module")
def empresas():
    return cargar()

# test para verificar que la función comparar devuelve el grupo y resto correctos 
# para una empresa específica y un conjunto de palancas movidas.
def test_aguinaldo_muestra_la_prima_vacacional_con_conteos_del_guion(empresas):
    resultado = comparar(empresas, "COMPAÑIA 36", {"aguinaldo_op": 20})
    grupo = empresas.loc[empresas["empresa"].isin(resultado["grupo"]["ids"])]
    resto = empresas.loc[empresas["empresa"].isin(resultado["resto"]["ids"])]

    diferencias = diferencias_principales(
        grupo,
        resto,
        palancas_movidas={"aguinaldo_op": 20},
        referencia=empresas,
    )

    prima = next(
        diferencia
        for diferencia in diferencias
        if diferencia["texto"] == "prima vacacional de 50% o más"
    )
    assert prima["grupo"] == "16 de 22"
    assert prima["resto"] == "4 de 16"
    assert len(diferencias) == 2
    assert all("aguinaldo" not in diferencia["texto"] for diferencia in diferencias)

#Se hace test de columnas numéricas para verificar que la función diferencias_principales 
# calcula correctamente las medianas y proporciones de "sí" en los grupos y resto, 
# y que devuelve los n rasgos más distintos entre ellos.
def test_columnas_numericas_reportan_medianas():
    grupo = pd.DataFrame(
        {
            "empresa": ["A", "B"],
            "sal_dia_ini": [10.0, 12.0],
            "comedor": ["Sí", "Sí"],
        }
    )
    resto = pd.DataFrame(
        {
            "empresa": ["C", "D"],
            "sal_dia_ini": [2.0, 4.0],
            "comedor": ["No", "No"],
        }
    )

    diferencias = diferencias_principales(grupo, resto)

    salario = next(item for item in diferencias if item["texto"] == "salario inicial mediano")
    comedor = next(item for item in diferencias if item["texto"] == "ofrecen comedor")
    assert salario["grupo"] == 11.0
    assert salario["resto"] == 3.0
    assert comedor["grupo"] == "2 de 2"
    assert comedor["resto"] == "0 de 2"

# test para verificar que la función diferencias_principales maneja 
# correctamente los casos en los que n es cero o negativo, 
# devolviendo una lista vacía o lanzando un ValueError según corresponda.
def test_n_cero_devuelve_lista_vacia_y_n_negativo_es_invalido():
    vacio = pd.DataFrame(columns=["empresa"])

    assert diferencias_principales(vacio, vacio, n=0) == []
    with pytest.raises(ValueError, match="n debe ser"):
        diferencias_principales(vacio, vacio, n=-1)
