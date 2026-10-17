"""Los 5 fixtures guardados son lo que hoy produce el motor real. Dueño: Juanes.

Prueba de regresión: si alguien cambia el motor y las cifras de un fixture se
mueven, esta prueba falla y avisa cuál. Arreglo: correr
    python scripts/regenerar_fixtures.py
revisar en la terminal qué cambió y, si el cambio es correcto, subir los fixtures nuevos.
"""
import json

import pytest

from config import RUTA_FIXTURES
from motor.datos import cargar
from scripts.correr_combinaciones import cargar_supuestos
from scripts.regenerar_fixtures import FIXTURES, construir, diferencias


@pytest.fixture(scope="module")
def empresas():
    return cargar()


@pytest.mark.parametrize("definicion", FIXTURES, ids=lambda d: d["archivo"])
def test_fixture_igual_al_motor(empresas, definicion):
    guardado = json.loads((RUTA_FIXTURES / definicion["archivo"]).read_text(encoding="utf-8"))
    nuevo = construir(empresas, definicion, cargar_supuestos())
    assert diferencias(guardado, nuevo) == []