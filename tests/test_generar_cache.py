"""Pruebas de scripts/generar_cache.py sin llamar a la IA (cliente falso). Dueño: Julian."""
import pytest

from ia.cache import buscar, cargar, llave
from ia.plantilla import plantilla
from ia.prompts import armar_mensaje
from motor.datos import cargar as cargar_empresas
from scripts import generar_cache as gc
from tests.test_explicar import ClienteFalso

SUPUESTOS = {"costo_por_baja": 15000, "costo_ruta_mensual": 35000}


@pytest.fixture(autouse=True)
def cache_temporal(monkeypatch, tmp_path):
    """Nunca se toca el data/processed/cache.json real."""
    monkeypatch.setattr("config.RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setattr("config.PAUSA_ESCRITURA_SEG", 0)


@pytest.fixture(scope="module")
def secuencias():
    return gc.armar_secuencias(gc.cargar_casos(), cargar_empresas(), SUPUESTOS)


class ClienteEco(ClienteFalso):
    """Responde a cada estado con su plantilla, que siempre pasa el validador.

    Así la prueba revisa el recorrido completo (secuencias -> precalcular -> caché)
    sin depender de lo que escriba la IA de verdad.
    """

    def __init__(self, secuencias):
        super().__init__()
        self.respuestas = {}
        for secuencia in secuencias:
            anterior = None
            for estado in secuencia:
                self.respuestas[armar_mensaje(estado, anterior)] = plantilla(estado)
                anterior = estado

    def stream(self, **kwargs):
        self.datos = {"trozos": [self.respuestas[kwargs["messages"][0]["content"]]]}
        return super().stream(**kwargs)


def test_hay_una_secuencia_por_historia_y_una_por_cada_caso(secuencias):
    casos = gc.cargar_casos()
    assert len(secuencias) == len(gc.SECUENCIAS) + len(casos)
    assert len(casos) == 20


def test_el_guion_termina_con_el_costo_por_baja_al_doble(secuencias):
    guion = secuencias[0]
    assert [e["grupo"]["n"] for e in guion] == [22, 16, 5, 5]
    assert guion[-1]["pesos"]["supuestos"]["costo_por_baja"] == 30000
    assert guion[-1]["pesos"]["costo_brecha_anual"] == pytest.approx(2 * guion[-2]["pesos"]["costo_brecha_anual"], rel=0.01)


def test_cada_paso_se_explica_con_el_anterior_de_su_historia(secuencias):
    llaves = gc.llaves_de(secuencias)
    g2, g1 = secuencias[0][1], secuencias[0][0]
    assert llave(g2, g1) in llaves
    assert "COMPAÑIA 15|sal_dia_ini=350|15000 <- COMPAÑIA 15|sal_dia_ini=340|15000" in llaves


def test_las_llaves_no_se_repiten(secuencias):
    llaves = gc.llaves_de(secuencias)
    assert len(llaves) == len(set(llaves)) == 26


def test_generar_llena_el_cache_y_la_app_lo_encuentra(secuencias):
    total = gc.generar(secuencias, cliente=ClienteEco(secuencias))
    assert total["fallidas"] == []
    assert sorted(cargar()) == sorted(gc.llaves_de(secuencias))
    # Lo que haría la app en el paso 3 del guion: lo encuentra al instante con su anterior
    g2, g3 = secuencias[0][1], secuencias[0][2]
    assert buscar(g3, g2) == plantilla(g3)


def test_mostrar_no_llama_a_la_ia(capsys):
    assert gc.main(["--mostrar"]) == 0
    assert "faltan 26" in capsys.readouterr().out
