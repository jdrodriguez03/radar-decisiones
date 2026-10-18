"""Pruebas del interruptor de emergencia MODO_DEMO. Dueño: Julian."""
import json

import pytest

from config import RUTA_FIXTURES
from ia.cache import guardar, llave
from ia.explicar import explicar, modo_demo
from ia.plantilla import plantilla
from tests.test_explicar import ClienteFalso

TEXTO_01 = "Las 22 empresas que ya dan 20 días de aguinaldo pierden 22% al año; las demás, 53%."


@pytest.fixture(autouse=True)
def entorno_limpio(monkeypatch, tmp_path):
    """Caché temporal, sin efecto de escritura y con MODO_DEMO apagado al empezar cada prueba."""
    monkeypatch.setattr("config.RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setattr("config.PAUSA_ESCRITURA_SEG", 0)
    monkeypatch.delenv("MODO_DEMO", raising=False)


def estado():
    return json.loads((RUTA_FIXTURES / "01_aguinaldo.json").read_text(encoding="utf-8"))


class ClienteTrampa:
    """Si alguien llama a la API, la prueba falla: en MODO_DEMO eso nunca debe pasar."""

    def __init__(self):
        self.messages = self

    def stream(self, **kwargs):
        raise AssertionError("MODO_DEMO llamó a la API")


# --- El interruptor ---

@pytest.mark.parametrize("valor", ["1", "si", "sí", "true", "TRUE", " 1 ", "on"])
def test_valores_que_lo_encienden(monkeypatch, valor):
    monkeypatch.setenv("MODO_DEMO", valor)
    assert modo_demo() is True


@pytest.mark.parametrize("valor", ["", "0", "no", "false", "apagado"])
def test_valores_que_lo_dejan_apagado(monkeypatch, valor):
    monkeypatch.setenv("MODO_DEMO", valor)
    assert modo_demo() is False


def test_por_defecto_esta_apagado():
    assert modo_demo() is False


# --- Lo que hace en la explicación ---

def test_encendido_y_sin_cache_sale_la_plantilla_sin_llamar_a_la_api(monkeypatch):
    monkeypatch.setenv("MODO_DEMO", "1")
    e = estado()
    texto = "".join(explicar(e, None, cliente=ClienteTrampa()))
    assert texto == plantilla(estado())
    assert e["explicacion"]["fuente"] == "plantilla"


def test_encendido_y_con_cache_sale_el_caché(monkeypatch):
    monkeypatch.setenv("MODO_DEMO", "1")
    e = estado()
    guardar({llave(e): {"texto": TEXTO_01}})
    texto = "".join(explicar(e, None, cliente=ClienteTrampa()))
    assert texto == TEXTO_01
    assert e["explicacion"]["fuente"] == "cache"


def test_apagado_la_ia_responde_en_vivo():
    e = estado()
    texto = "".join(explicar(e, None, cliente=ClienteFalso(trozos=[TEXTO_01]), limite=2))
    assert texto == TEXTO_01
    assert e["explicacion"]["fuente"] == "llm"
