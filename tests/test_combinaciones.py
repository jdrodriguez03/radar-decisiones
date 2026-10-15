"""Revisa que combinaciones.yaml esté completo y bien escrito. Dueño: Juanes."""
import pandas as pd
import pytest

from scripts.correr_combinaciones import (
    cambio_de,
    cargar_casos,
    fila_de_estado,
    perfil_de_empresa,
    pesos,
    validar_caso,
)


def test_son_20_casos_con_id_unico():
    casos = cargar_casos()
    assert len(casos) == 20
    assert len({c["id"] for c in casos}) == 20


def test_estan_los_tres_pasos_del_guion():
    guion = [c for c in cargar_casos() if c["tipo"] == "guion"]
    assert [c["id"] for c in guion] == ["G1", "G2", "G3"]


def test_palanca_inexistente_falla():
    with pytest.raises(ValueError):
        validar_caso({"id": "X", "empresa": "COMPAÑIA 36", "palancas": {"bono": 1}})


def test_valor_fuera_de_rango_falla():
    with pytest.raises(ValueError):
        validar_caso({"id": "X", "empresa": "COMPAÑIA 36", "palancas": {"aguinaldo_op": 50}})


def test_formato_pesos():
    assert pesos(6341580) == "$6.3 M"
    assert pesos(-5_100_000) == "−$5.1 M"

# --- Día 7: del DataFrame al perfil y del contrato a la fila -------------------
# Estas pruebas NO llaman al motor: usan una tabla de 1 empresa y un contrato
# escrito a mano, para probar solo el código de Juanes.
 
EMPRESAS = pd.DataFrame([{
    "empresa": "COMPAÑIA 36", "plantilla_op": 1438.0, "banda": "grande",
    "sal_dia_ini": 323.61, "aguinaldo_op": 15.0, "prima_vac_op": 0.25,
    "vales_op": 0.09, "rutas_x100": 2.85,
    "rot_anual": 0.516, "bajas_menos3m": 0.4, "aus_inj_op": float("nan"),
}])
 
 
def test_perfil_usa_nombres_del_contrato_y_none_si_falta():
    perfil = perfil_de_empresa(EMPRESAS, "COMPAÑIA 36")
    assert perfil["plantilla_op"] == 1438
    assert perfil["indicadores"] == {"rot_anual": 0.516, "rot_temprana": 0.4, "ausentismo": None}
 
 
def test_cambio_es_la_ultima_palanca_movida():
    perfil = perfil_de_empresa(EMPRESAS, "COMPAÑIA 36")
    assert cambio_de(perfil, {"aguinaldo_op": 20, "prima_vac_op": 0.5}) == {
        "palanca": "prima_vac_op", "de": 0.25, "a": 0.5,
    }
    assert cambio_de(perfil, {}) is None
 
 
def _estado(n_grupo, rot_grupo, n_resto, rot_resto):
    return {
        "empresa": {"indicadores": {"rot_anual": 0.516}},
        "grupo": {"n": n_grupo, "completado": False, "indicadores": {"rot_anual": rot_grupo}},
        "resto": {"n": n_resto,
                  "indicadores": None if rot_resto is None else {"rot_anual": rot_resto}},
        "senal": {"etiqueta": "clara", "p": 0.047},
        "pesos": {"costo_medida_anual": 2326756, "costo_brecha_anual": 6341580},
    }
 
 
def test_fila_lee_el_contrato_y_revisa_el_guion():
    caso = {"id": "G1", "empresa": "COMPAÑIA 36", "palancas": {"aguinaldo_op": 20},
            "esperado": {"n_grupo": 22, "rot_grupo": 0.22, "rot_resto": 0.53}}
    fila = fila_de_estado(caso, _estado(22, 0.222, 16, 0.534))
    assert fila["alertas"] == []
    assert fila["revision_guion"] == "coincide"
    assert fila["costo_brecha"] == 6341580
 
 
def test_resto_vacio_no_rompe_y_marca_alerta():
    caso = {"id": "X", "empresa": "COMPAÑIA 36", "palancas": {"vales_op": 0.06}}
    fila = fila_de_estado(caso, _estado(39, 0.36, 0, None))
    assert fila["rot_resto"] is None
    assert fila["alertas"] == ["resto con menos de 5"]
 
 
def test_grupo_que_rota_mas_marca_alerta():
    caso = {"id": "X", "empresa": "COMPAÑIA 36", "palancas": {"rutas_x100": 10.8}}
    fila = fila_de_estado(caso, _estado(5, 0.49, 33, 0.36))
    assert fila["alertas"] == ["el grupo rota más que el resto"]