"""Los 5 fixtures cumplen el contrato y sus pesos cuadran con pesos.py. Dueño: Juanes."""
import json

import pytest

from config import RUTA_FIXTURES
from contrato.modelo import validar
from motor.pesos import costo_brecha, costo_medida

ARCHIVOS = sorted(RUTA_FIXTURES.glob("*.json"))


def cargar(ruta):
    return json.loads(ruta.read_text(encoding="utf-8"))


def test_hay_cinco_fixtures():
    assert len(ARCHIVOS) == 5


@pytest.mark.parametrize("ruta", ARCHIVOS, ids=lambda r: r.stem)
def test_fixture_valida(ruta):
    validar(cargar(ruta))


@pytest.mark.parametrize("ruta", ARCHIVOS, ids=lambda r: r.stem)
def test_pesos_del_fixture(ruta):
    e = cargar(ruta)
    supuestos = {"costo_por_baja": 15000, "costo_ruta_mensual": 35000}
    medida = costo_medida(e["empresa"], e["palancas_movidas"], supuestos)
    brecha = costo_brecha(e["empresa"]["indicadores"]["rot_anual"],
                          e["grupo"]["indicadores"]["rot_anual"],
                          e["empresa"]["plantilla_op"], 15000)
    assert round(medida) == pytest.approx(e["pesos"]["costo_medida_anual"], abs=1)
    assert round(brecha) == pytest.approx(e["pesos"]["costo_brecha_anual"], abs=1)
