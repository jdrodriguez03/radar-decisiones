"""Pruebas del selector de empresa (sin abrir la pantalla). Dueño: Juanes."""
import math
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from config import PALANCAS
from contrato.modelo import Empresa
from motor.datos import cargar
from ui.selector import (
    MI_EMPRESA_ID,
    ids_ordenados,
    palancas_sin_dato,
    perfil_demo,
    perfil_mi_empresa,
    validar_captura,
)


def tabla_falsa():
    """Seis empresas con columna 'empresa', como el parquet real."""
    ids = ["COMPAÑIA 10", "COMPAÑIA 2", "COMPAÑIA 15", "COMPAÑIA 36", "COMPAÑIA 29", "COMPAÑIA 1"]
    filas = []
    for i, empresa_id in enumerate(ids):
        fila = {col: minimo for col, (minimo, _maximo, _paso) in PALANCAS.items()}
        fila.update(empresa=empresa_id, plantilla_op=100.0 + i, rot_anual=0.3,
                    bajas_menos3m=0.5, aus_inj_op=float("nan"))
        filas.append(fila)
    tabla = pd.DataFrame(filas)
    tabla.loc[tabla["empresa"] == "COMPAÑIA 10", "vales_op"] = float("nan")
    return tabla


def captura_valida():
    return {
        "plantilla_op": 800,
        "rot_mensual_pct": 4.3,
        "palancas": {col: minimo for col, (minimo, _maximo, _paso) in PALANCAS.items()},
    }


def test_recomendadas_arriba_y_resto_en_orden():
    assert ids_ordenados(tabla_falsa()) == [
        "COMPAÑIA 36", "COMPAÑIA 29", "COMPAÑIA 15",
        "COMPAÑIA 1", "COMPAÑIA 2", "COMPAÑIA 10",
    ]


def test_perfil_demo_cumple_el_contrato():
    perfil = perfil_demo(tabla_falsa(), "COMPAÑIA 36")
    Empresa.model_validate(perfil)
    assert perfil["plantilla_op"] == 103
    assert set(perfil["palancas"]) == set(PALANCAS)
    assert perfil["indicadores"]["ausentismo"] is None  # NaN pasa a None


def test_palanca_sin_dato_se_omite():
    perfil = perfil_demo(tabla_falsa(), "COMPAÑIA 10")
    Empresa.model_validate(perfil)
    assert "vales_op" not in perfil["palancas"]
    assert palancas_sin_dato(perfil) == ["vales_op"]


def test_captura_valida_no_tiene_errores():
    assert validar_captura(captura_valida()) == []


def test_captura_fuera_de_rango_da_mensajes_claros():
    datos = captura_valida()
    datos["plantilla_op"] = 0
    datos["palancas"]["aguinaldo_op"] = PALANCAS["aguinaldo_op"][1] + 10
    errores = validar_captura(datos)
    assert len(errores) == 2
    assert errores[0].startswith("Plantilla operativa")
    assert "aguinaldo" in errores[1].lower()


def test_perfil_mi_empresa_cumple_el_contrato():
    perfil = perfil_mi_empresa(captura_valida())
    Empresa.model_validate(perfil)
    assert perfil["id"] == MI_EMPRESA_ID
    assert math.isclose(perfil["indicadores"]["rot_anual"], 0.516)
    assert perfil["indicadores"]["rot_temprana"] is None
    assert perfil["indicadores"]["ausentismo"] is None


def test_perfil_mi_empresa_con_errores_lanza_error():
    datos = captura_valida()
    datos["rot_mensual_pct"] = 80
    with pytest.raises(ValueError):
        perfil_mi_empresa(datos)


def test_compania_36_con_datos_reales():
    perfil = perfil_demo(cargar(), "COMPAÑIA 36")
    assert perfil["plantilla_op"] == 1438
    assert perfil["palancas"]["aguinaldo_op"] == 15
    assert perfil["palancas"]["prima_vac_op"] == pytest.approx(0.25)
    assert perfil["indicadores"]["rot_anual"] == pytest.approx(0.516)


def test_las_40_empresas_cumplen_el_contrato():
    empresas = cargar()
    for empresa_id in ids_ordenados(empresas):
        Empresa.model_validate(perfil_demo(empresas, empresa_id))


def test_mi_empresa_se_envia_y_muestra_el_comparativo():
    app = Path(__file__).resolve().parents[1] / "app.py"
    at = AppTest.from_file(app, default_timeout=30).run()
    at.radio[0].set_value("Mi empresa").run()

    valores = [800, 4.3, 330, 22, 50, 10, 3]
    assert len(at.number_input) == len(valores)
    for campo, valor in zip(at.number_input, valores):
        campo.set_value(valor)
    at.run()

    next(boton for boton in at.button if boton.label == "Usar mi empresa").click().run()

    assert not at.exception
    assert not at.info
    assert any("Comparando con 40 empresas reales" in item.value for item in at.markdown)


def test_botones_mas_y_menos_actualizan_las_palancas():
    app = Path(__file__).resolve().parents[1] / "app.py"
    at = AppTest.from_file(app, default_timeout=30).run()
    valor_inicial = next(slider.value for slider in at.slider if slider.key == "valor_aguinaldo_op")

    next(boton for boton in at.button if boton.key == "mas_aguinaldo_op").click().run()
    valor_mayor = next(slider.value for slider in at.slider if slider.key == "valor_aguinaldo_op")
    assert valor_mayor == valor_inicial + 1
    assert any(item.value == '<div class="palanca-valor">16</div>' for item in at.markdown)

    next(boton for boton in at.button if boton.key == "menos_aguinaldo_op").click().run()
    valor_final = next(slider.value for slider in at.slider if slider.key == "valor_aguinaldo_op")
    assert valor_final == valor_inicial
    assert any(item.value == '<div class="palanca-valor">15</div>' for item in at.markdown)
