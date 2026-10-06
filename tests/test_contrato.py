"""Dueño: Juanes (D). Pruebas del contrato."""
import json

import pytest
from pydantic import ValidationError

from config import RUTA_EJEMPLO
from contrato.modelo import validar


def cargar_ejemplo():
    return json.loads(RUTA_EJEMPLO.read_text(encoding="utf-8"))


def test_ejemplo_valida():
    estado = validar(cargar_ejemplo())
    assert estado.grupo.n == 22
    assert estado.empresa.id == "COMPAÑIA 36"


def test_sin_grupo_falla():
    datos = cargar_ejemplo()
    del datos["grupo"]
    with pytest.raises(ValidationError):
        validar(datos)