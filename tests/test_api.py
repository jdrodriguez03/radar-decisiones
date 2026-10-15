import json

import pytest

from config import PALANCAS, RUTA_EJEMPLO, RUTA_SUPUESTOS
from contrato.modelo import validar
from motor import api
from motor.api import calcular_estado
from motor.datos import cargar
from ui.selector import perfil_demo, perfil_mi_empresa


def captura_personal(plantilla=800):
    return perfil_mi_empresa(
        {
            "plantilla_op": plantilla,
            "rot_mensual_pct": 4.3,
            "palancas": {
                columna: valores[0] for columna, valores in PALANCAS.items()
            },
        }
    )


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


def test_mi_empresa_externa_con_indicadores_no_capturados_cumple_el_contrato():
    empresas = cargar()
    perfil = captura_personal()
    supuestos = json.loads(RUTA_SUPUESTOS.read_text(encoding="utf-8"))

    estado = calcular_estado(empresas, perfil, {}, None, supuestos)

    validar(estado)
    assert estado["empresa"]["id"] == perfil["id"]
    assert estado["empresa"]["indicadores"]["rot_temprana"] is None
    assert estado["empresa"]["indicadores"]["ausentismo"] is None
    assert estado["grupo"]["n"] + estado["resto"]["n"] == len(empresas)
    assert perfil["id"] not in estado["grupo"]["ids"]
    assert perfil["id"] not in estado["resto"]["ids"]


def test_solo_tamano_filtra_la_banda_de_mi_empresa():
    empresas = cargar()
    perfil = captura_personal(plantilla=800)
    supuestos = json.loads(RUTA_SUPUESTOS.read_text(encoding="utf-8"))
    ids_grandes = sorted(empresas.loc[empresas["banda"].eq("grande"), "empresa"])

    estado = calcular_estado(
        empresas,
        perfil,
        {},
        None,
        supuestos,
        solo_tamano=True,
    )

    assert estado["grupo"]["ids"] == ids_grandes
    assert estado["grupo"]["n"] == len(ids_grandes)
    assert estado["resto"]["n"] == 0


@pytest.mark.parametrize(
    "extremo",
    [
        {columna: valores[0] for columna, valores in PALANCAS.items()},
        {columna: valores[1] for columna, valores in PALANCAS.items()},
    ],
    ids=["todas-minimo", "todas-maximo"],
)
def test_extremos_de_todas_las_palancas_no_lanzan_error(extremo):
    empresas = cargar()
    perfil = perfil_demo(empresas, "COMPAÑIA 36")
    supuestos = json.loads(RUTA_SUPUESTOS.read_text(encoding="utf-8"))
    palanca = "aguinaldo_op"
    cambio = {
        "palanca": palanca,
        "de": perfil["palancas"][palanca],
        "a": extremo[palanca],
    }

    estado = calcular_estado(empresas, perfil, extremo, cambio, supuestos)

    validar(estado)
    assert estado["palancas_movidas"] == extremo
    assert estado["grupo"]["n"] >= 1


def test_bajar_una_palanca_por_debajo_del_valor_actual_no_lanza_error():
    empresas = cargar()
    perfil = perfil_demo(empresas, "COMPAÑIA 36")
    supuestos = json.loads(RUTA_SUPUESTOS.read_text(encoding="utf-8"))
    valor_nuevo = PALANCAS["sal_dia_ini"][0]

    estado = calcular_estado(
        empresas,
        perfil,
        {"sal_dia_ini": valor_nuevo},
        {
            "palanca": "sal_dia_ini",
            "de": perfil["palancas"]["sal_dia_ini"],
            "a": valor_nuevo,
        },
        supuestos,
    )

    validar(estado)
    assert valor_nuevo < perfil["palancas"]["sal_dia_ini"]
    assert estado["palancas_movidas"]["sal_dia_ini"] == valor_nuevo


def test_resultados_repetidos_usan_cache_y_se_devuelven_sin_alias(monkeypatch):
    empresas = cargar()
    perfil = perfil_demo(empresas, "COMPAÑIA 36")
    supuestos = {"costo_por_baja": 987654321, "costo_ruta_mensual": 35000}
    argumentos = (
        empresas,
        perfil,
        {"aguinaldo_op": 20.0},
        {"palanca": "aguinaldo_op", "de": 15.0, "a": 20.0},
        supuestos,
    )
    comparar_original = api.comparar
    llamadas = 0

    def contar_comparaciones(*args, **kwargs):
        nonlocal llamadas
        llamadas += 1
        return comparar_original(*args, **kwargs)

    with api._ESTADOS_CACHE_LOCK:
        api._ESTADOS_CACHE.clear()
    monkeypatch.setattr(api, "comparar", contar_comparaciones)
    primer_estado = calcular_estado(*argumentos)
    primer_estado["grupo"]["ids"].clear()
    segundo_estado = calcular_estado(*argumentos)

    assert llamadas == 1
    assert segundo_estado["grupo"]["n"] == len(segundo_estado["grupo"]["ids"])


def test_cambios_de_supuestos_perfil_o_datos_no_reutilizan_resultado_incorrecto():
    empresas = cargar()
    perfil = perfil_demo(empresas, "COMPAÑIA 36")
    supuestos = {"costo_por_baja": 15000.0, "costo_ruta_mensual": 35000.0}
    movidas = {"aguinaldo_op": 20.0}
    cambio = {"palanca": "aguinaldo_op", "de": 15.0, "a": 20.0}

    with api._ESTADOS_CACHE_LOCK:
        api._ESTADOS_CACHE.clear()
    estado_base = calcular_estado(empresas, perfil, movidas, cambio, supuestos)

    supuestos_mayores = {**supuestos, "costo_por_baja": 30000.0}
    estado_otro_supuestos = calcular_estado(
        empresas, perfil, movidas, cambio, supuestos_mayores
    )
    assert estado_otro_supuestos["pesos"]["costo_brecha_anual"] == pytest.approx(
        estado_base["pesos"]["costo_brecha_anual"] * 2
    )

    perfil_modificado = {**perfil, "indicadores": {
        **perfil["indicadores"],
        "rot_anual": perfil["indicadores"]["rot_anual"] + 0.1,
    }}
    estado_otro_perfil = calcular_estado(
        empresas, perfil_modificado, movidas, cambio, supuestos
    )
    assert estado_otro_perfil["empresa"]["indicadores"]["rot_anual"] == pytest.approx(
        perfil_modificado["indicadores"]["rot_anual"]
    )
    assert estado_otro_perfil["pesos"]["costo_brecha_anual"] != (
        estado_base["pesos"]["costo_brecha_anual"]
    )

    empresas["rot_anual"] = empresas["rot_anual"] + 0.1
    estado_datos_modificados = calcular_estado(
        empresas, perfil, movidas, cambio, supuestos
    )
    assert estado_datos_modificados["grupo"]["indicadores"]["rot_anual"] == pytest.approx(
        estado_base["grupo"]["indicadores"]["rot_anual"] + 0.1
    )


def test_huella_incluye_motivos_y_omite_columnas_ajenas_al_resultado():
    empresas = cargar().copy(deep=True)
    with api._ESTADOS_CACHE_LOCK:
        api._HUELLAS_DATAFRAME.clear()

    huella_inicial = api._huella_dataframe(empresas)
    empresas.loc[empresas.index[0], "orden_periodo"] += 1
    assert api._huella_dataframe(empresas) == huella_inicial

    empresas.loc[empresas.index[0], "m_sueldo"] += 0.01
    assert api._huella_dataframe(empresas) != huella_inicial
