import json
import time

import pytest

from config import RUTA_FIXTURES
from ia.cache import buscar, cargar, guardar, llave
from ia.explicar import explicar
from ia.precalcular import precalcular
from tests.test_explicar import ClienteFalso


@pytest.fixture(autouse=True)
def cache_temporal(monkeypatch, tmp_path):
    """Las pruebas nunca leen ni escriben el data/processed/cache.json real."""
    monkeypatch.setattr("config.RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setattr("config.PAUSA_ESCRITURA_SEG", 0)  # el efecto de escritura no hace falta en las pruebas
    return tmp_path / "cache.json"


def cargar_fixture(nombre):
    return json.loads((RUTA_FIXTURES / f"{nombre}.json").read_text(encoding="utf-8"))


TEXTO_01 = "Las 22 empresas que ya dan 20 días de aguinaldo pierden 22% al año; las demás, 53%."
TEXTO_02 = "Con la prima de 50% y el aguinaldo de 20 días, quedan 16 empresas; las demás pierden 43%, antes 53%."


# --- La llave ---

def test_llave_con_empresa_palancas_y_costo():
    assert llave(cargar_fixture("01_aguinaldo")) == "COMPAÑIA 36|aguinaldo_op=20|15000"


def test_20_y_20_punto_0_dan_la_misma_llave():
    estado = cargar_fixture("01_aguinaldo")
    otra = cargar_fixture("01_aguinaldo")
    otra["palancas_movidas"]["aguinaldo_op"] = 20.0
    assert llave(estado) == llave(otra)


def test_el_costo_por_baja_cambia_la_llave():
    estado = cargar_fixture("01_aguinaldo")
    caro = cargar_fixture("01_aguinaldo")
    caro["pesos"]["supuestos"]["costo_por_baja"] = 30000
    assert llave(estado) != llave(caro)


def test_el_paso_anterior_va_en_la_llave():
    clave = llave(cargar_fixture("02_prima"), cargar_fixture("01_aguinaldo"))
    assert clave.endswith("<- COMPAÑIA 36|aguinaldo_op=20|15000")


def test_el_estado_inicial_como_anterior_no_cuenta():
    # Misma regla que armar_mensaje: después del estado inicial es una primera comparación
    assert llave(cargar_fixture("01_aguinaldo"), cargar_fixture("05_inicial")) == llave(cargar_fixture("01_aguinaldo"))


def test_un_estado_incompleto_no_rompe_la_busqueda():
    estado = cargar_fixture("01_aguinaldo")
    del estado["pesos"]
    assert buscar(estado, None, {}) is None


# --- Leer y buscar ---

def test_sin_archivo_el_cache_esta_vacio():
    assert cargar() == {}


def test_un_cache_danado_no_tumba_la_demo(cache_temporal):
    cache_temporal.write_text("{esto no es json", encoding="utf-8")
    assert cargar() == {}


def test_buscar_con_y_sin_paso_anterior():
    e01, e02 = cargar_fixture("01_aguinaldo"), cargar_fixture("02_prima")
    cache = {llave(e02, e01): {"texto": TEXTO_02}}
    assert buscar(e02, e01, cache) == TEXTO_02


def test_si_no_esta_el_paso_exacto_usa_el_texto_sin_anterior():
    e01, e02 = cargar_fixture("01_aguinaldo"), cargar_fixture("02_prima")
    sin_antes = "Con la prima de 50% y el aguinaldo de 20 días, quedan 16 empresas."
    cache = {llave(e02): {"texto": sin_antes}}
    assert buscar(e02, e01, cache) == sin_antes


def test_un_texto_con_cifras_viejas_se_descarta():
    # Si el motor cambia una cifra después de generar el caché, el validador lo nota
    estado = cargar_fixture("01_aguinaldo")
    cache = {llave(estado): {"texto": "Las 22 empresas pierden 19% al año."}}
    assert buscar(estado, None, cache) is None


# --- explicar usa el caché ---

def test_explicar_responde_al_instante_desde_el_cache():
    estado = cargar_fixture("01_aguinaldo")
    guardar({llave(estado): {"texto": TEXTO_01}})
    cliente = ClienteFalso(trozos=["no ", "debería ", "llamarse"], espera=5)  # si llamara a la API, tardaría 5 s
    inicio = time.perf_counter()
    texto = "".join(explicar(estado, None, cliente=cliente))
    assert time.perf_counter() - inicio < 0.5
    assert texto == TEXTO_01
    assert estado["explicacion"] == {"fuente": "cache", "texto": TEXTO_01}


def test_cache_vacio_obliga_a_usar_la_api():
    estado = cargar_fixture("01_aguinaldo")
    guardar({llave(estado): {"texto": TEXTO_01}})
    "".join(explicar(estado, None, cliente=ClienteFalso(trozos=[TEXTO_01]), cache={}))
    assert estado["explicacion"]["fuente"] == "llm"


# --- precalcular ---

def test_precalcular_guarda_el_guion_con_su_paso_anterior():
    e01, e02 = cargar_fixture("01_aguinaldo"), cargar_fixture("02_prima")
    original = cargar_fixture("02_prima")
    respuestas = iter([[TEXTO_01], [TEXTO_02]])

    class ClientePorTurnos(ClienteFalso):
        def stream(self, **kwargs):
            self.datos = {"trozos": next(respuestas)}
            return super().stream(**kwargs)

    resumen = precalcular([e01, e02], cliente=ClientePorTurnos())
    assert resumen["fallidas"] == []
    cache = cargar()
    assert cache[llave(e01)]["texto"] == TEXTO_01
    assert cache[llave(e02, e01)]["texto"] == TEXTO_02
    assert e02 == original  # precalcular trabaja sobre una copia: el estado original no se toca


def test_precalcular_no_guarda_cifras_inventadas():
    estado = cargar_fixture("01_aguinaldo")
    resumen = precalcular([estado], cliente=ClienteFalso(trozos=["Pierden 31 puntos menos."]))
    assert resumen["fallidas"] == [llave(estado)]
    assert cargar() == {}


def test_precalcular_no_repite_lo_que_ya_esta():
    estado = cargar_fixture("01_aguinaldo")
    guardar({llave(estado): {"texto": TEXTO_01}})
    resumen = precalcular([estado], cliente=ClienteFalso(trozos=["otro texto"]))
    assert resumen["ya_estaban"] == [llave(estado)]
    assert cargar()[llave(estado)]["texto"] == TEXTO_01


def test_precalcular_rehace_un_texto_que_ya_no_es_valido():
    # Si el motor cambia una cifra, el texto guardado queda vencido: se pide de nuevo
    estado = cargar_fixture("01_aguinaldo")
    guardar({llave(estado): {"texto": "Las 31 empresas que ya lo hacen pierden 9% al año."}})
    resumen = precalcular([estado], cliente=ClienteFalso(trozos=[TEXTO_01]))
    assert resumen["guardadas"] == [llave(estado)]
    assert cargar()[llave(estado)]["texto"] == TEXTO_01


def test_precalcular_borra_un_texto_vencido_si_no_logra_reemplazarlo():
    estado = cargar_fixture("01_aguinaldo")
    guardar({llave(estado): {"texto": "Las 31 empresas que ya lo hacen pierden 9% al año."}})
    resumen = precalcular([estado], cliente=ClienteFalso(trozos=[], error=ConnectionError("sin internet")))
    assert resumen["fallidas"] == [llave(estado)]
    assert cargar() == {}

