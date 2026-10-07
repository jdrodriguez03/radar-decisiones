"""Pruebas de los costos con las cifras del guion. Dueño: Juanes."""
import pytest

from motor.pesos import costo_brecha, costo_medida

C36 = {
    "plantilla_op": 1438,
    "palancas": {"sal_dia_ini": 323.61, "aguinaldo_op": 15, "prima_vac_op": 0.25,
                 "vales_op": 0.09, "rutas_x100": 2.85},
}
SUPUESTOS = {"costo_por_baja": 15000, "costo_ruta_mensual": 35000}


def test_aguinaldo():
    assert round(costo_medida(C36, {"aguinaldo_op": 20}, SUPUESTOS)) == 2_326_756


def test_aguinaldo_y_prima():
    movidas = {"aguinaldo_op": 20, "prima_vac_op": 0.5}
    assert round(costo_medida(C36, movidas, SUPUESTOS)) == 3_722_809


def test_tres_pasos_del_guion():
    movidas = {"aguinaldo_op": 20, "prima_vac_op": 0.5, "sal_dia_ini": 350}
    assert round(costo_medida(C36, movidas, SUPUESTOS)) == 17_574_129


def test_sin_palancas_movidas():
    assert costo_medida(C36, {}, SUPUESTOS) == 0


def test_rutas_usa_costo_mensual():
    # 1 ruta más por cada 100 operativos = 14.38 rutas × $35,000 × 12 meses
    costo = costo_medida(C36, {"rutas_x100": 3.85}, SUPUESTOS)
    assert costo == pytest.approx(14.38 * 35000 * 12)


def test_brecha():
    assert round(costo_brecha(0.516, 0.222, 1438, 15000)) == 6_341_580


def test_brecha_se_duplica_con_costo_doble():
    assert round(costo_brecha(0.516, 0.222, 1438, 30000)) == 12_683_160


def test_brecha_cero_si_ya_rota_menos():
    assert costo_brecha(0.036, 0.42, 965, 15000) == 0
