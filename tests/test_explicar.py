import json
import time

import anthropic
import pytest

from config import RUTA_EJEMPLO, RUTA_FIXTURES
from contrato.modelo import validar
from ia.explicar import TEXTO_EMERGENCIA, explicar
from ia.plantilla import plantilla


class FlujoFalso:
    """Imita lo que devuelve cliente.messages.stream(...): un 'with' con text_stream."""

    def __init__(self, trozos, espera=0.0, error=None, pausa=0.0):
        self.trozos, self.espera, self.error, self.pausa = trozos, espera, error, pausa
        self.cerrado = False

    def close(self):
        self.cerrado = True

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    @property
    def text_stream(self):
        time.sleep(self.espera)  # lo que tarda en llegar la primera palabra
        if self.error:
            raise self.error
        for trozo in self.trozos:
            if self.cerrado:
                return
            yield trozo
            time.sleep(self.pausa)  # lo que tarda en llegar el siguiente trozo


class ClienteFalso:
    def __init__(self, **datos):
        self.messages = self
        self.datos = datos

    def stream(self, **kwargs):
        self.pedido = kwargs  # lo que se le mandó a la API, para revisarlo en la prueba
        self.flujo = FlujoFalso(**self.datos)  # se guarda para revisarlo en la prueba
        return self.flujo


@pytest.fixture(autouse=True)
def sin_cache_real(monkeypatch, tmp_path):
    """Cada prueba usa un caché vacío en una carpeta temporal, nunca data/processed/cache.json.

    Sin esto, cuando exista el caché real, explicar devolvería el texto guardado
    y las pruebas de la API falsa dejarían de probar la API.
    """
    monkeypatch.setattr("config.RUTA_CACHE", tmp_path / "cache.json")


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


class ClicNuevo(BaseException):
    """Imita la señal que lanza Streamlit cuando llega un clic nuevo (también es BaseException)."""


def test_clic_nuevo_a_mitad_del_texto_lo_detiene():
    estado = cargar_estado()
    antes = dict(estado["explicacion"])
    cliente = ClienteFalso(trozos=["Las ", "22 ", "empresas ", "pierden"], pausa=0.2)
    generador = explicar(estado, None, cliente=cliente, limite=1)
    assert next(generador) == "Las "
    generador.close()  # así llega un clic nuevo: nadie sigue leyendo este texto
    assert cliente.flujo.cerrado  # se cerró la conexión con la API
    assert estado["explicacion"] == antes  # el texto viejo no quedó guardado


def test_clic_nuevo_mientras_espera_la_primera_palabra():
    estado = cargar_estado()
    antes = dict(estado["explicacion"])
    cliente = ClienteFalso(trozos=["llega tarde"], espera=2.0)
    latidos = []

    def latido():
        latidos.append(1)
        if len(latidos) == 3:  # al tercer latido (0.3 s) llega el clic nuevo
            raise ClicNuevo()

    inicio = time.perf_counter()
    with pytest.raises(ClicNuevo):
        list(explicar(estado, None, cliente=cliente, limite=4, latido=latido))
    assert time.perf_counter() - inicio < 1  # no esperó los 4 s del límite
    assert estado["explicacion"] == antes
    
@pytest.mark.parametrize(
    "modelo, pensamiento",
    [
        ("claude-sonnet-5-5", {"type": "between_tools"}),
        ("claude-haiku-5-5", {"type": "disabled"}),
        ("claude-haiku-4-5-20251001", None),
    ],
)
def test_apaga_el_pensamiento_en_los_modelos_5(modelo, pensamiento):
    cliente = ClienteFalso(trozos=["Hola."])
    "".join(explicar(cargar_estado(), None, cliente=cliente, limite=1, modelo=modelo))
    assert cliente.pedido["model"] == modelo
    assert cliente.pedido.get("thinking") == pensamiento


class ClienteSinInternet:
    """Lanza el mismo error que da el SDK de Anthropic cuando no hay conexión."""

    def __init__(self):
        self.messages = self

    def stream(self, **kwargs):
        raise anthropic.APIConnectionError(request=None)


@pytest.mark.parametrize("nombre", ["01_aguinaldo", "02_prima", "03_salario", "04_ya_rota_menos", "05_inicial"])
def test_sin_internet_sale_la_plantilla_en_menos_de_un_segundo(nombre):
    estado = json.loads((RUTA_FIXTURES / f"{nombre}.json").read_text(encoding="utf-8"))
    inicio = time.perf_counter()
    texto = "".join(explicar(estado, None, cliente=ClienteSinInternet()))
    assert time.perf_counter() - inicio < 1
    assert texto == plantilla(estado)
    assert estado["explicacion"]["fuente"] == "plantilla"


def test_si_hasta_la_plantilla_falla_sale_un_texto_fijo():
    estado = cargar_estado()
    del estado["pesos"]  # un estado incompleto rompe la plantilla
    texto = "".join(explicar(estado, None, cliente=ClienteSinInternet()))
    assert texto == TEXTO_EMERGENCIA


def test_cifra_inventada_cae_a_la_plantilla():
    estado = cargar_estado()
    cliente = ClienteFalso(trozos=["Esas 22 empresas ", "pierden 31 puntos menos."])  # 31 no está en el JSON
    texto_en_pantalla = "".join(explicar(estado, None, cliente=cliente, limite=1))
    assert "31" in texto_en_pantalla  # ya se escribió en pantalla: explicar no puede borrarlo
    assert estado["explicacion"] == {"fuente": "plantilla", "texto": plantilla(cargar_estado())}


def test_texto_con_cifras_reales_se_queda():
    estado = cargar_estado()
    cliente = ClienteFalso(trozos=["Las 22 empresas ", "pierden 22% al año; las demás, 53%."])
    "".join(explicar(estado, None, cliente=cliente, limite=1))
    assert estado["explicacion"]["fuente"] == "llm"