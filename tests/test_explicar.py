import json
import time

from config import RUTA_EJEMPLO
from contrato.modelo import validar
from ia.explicar import explicar
from ia.plantilla import plantilla


class FlujoFalso:
    """Imita lo que devuelve cliente.messages.stream(...): un 'with' con text_stream."""

    def __init__(self, trozos, espera=0.0, error=None):
        self.trozos, self.espera, self.error = trozos, espera, error

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    @property
    def text_stream(self):
        time.sleep(self.espera)  # lo que tarda en llegar la primera palabra
        if self.error:
            raise self.error
        yield from self.trozos


class ClienteFalso:
    def __init__(self, **datos):
        self.messages = self
        self.datos = datos

    def stream(self, **kwargs):
        return FlujoFalso(**self.datos)


def cargar_estado():
    return json.loads(RUTA_EJEMPLO.read_text(encoding="utf-8"))


def test_si_la_ia_tarda_sale_la_plantilla():
    estado = cargar_estado()
    cliente = ClienteFalso(trozos=["Hola ", "mundo"], espera=1.0)  # tarda más que el límite
    texto = "".join(explicar(estado, None, cliente=cliente, limite=0.2))
    assert texto == plantilla(cargar_estado())
    assert estado["explicacion"]["fuente"] == "plantilla"


def test_si_la_api_falla_sale_la_plantilla():
    estado = cargar_estado()
    cliente = ClienteFalso(trozos=[], error=ConnectionError("sin internet"))
    texto = "".join(explicar(estado, None, cliente=cliente, limite=1))
    assert texto == plantilla(cargar_estado())
    assert estado["explicacion"]["fuente"] == "plantilla"


def test_si_la_ia_responde_a_tiempo_sale_su_texto():
    estado = cargar_estado()
    cliente = ClienteFalso(trozos=["Las 22 ", "empresas."])
    texto = "".join(explicar(estado, None, cliente=cliente, limite=1))
    assert texto == "Las 22 empresas."
    assert estado["explicacion"] == {"fuente": "llm", "texto": "Las 22 empresas."}
    validar(estado)  # el estado con la explicación nueva sigue cumpliendo el contrato