"""Cuando no hay con quién comparar. Dueño: Julian.

Error encontrado el 19 de octubre: al bajar una palanca hasta un nivel que tienen todas las empresas
(por ejemplo, COMPAÑIA 29 con aguinaldo de 26 a 15 días), el resto queda vacío y «Explicar» mostraba
el texto de emergencia, que parece una falla técnica.
"""
import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from ia.explicar import TEXTO_EMERGENCIA, explicar
from ia.plantilla import plantilla, sin_comparacion
from ia.reglas import revisar
from ia.validador import es_valido
from motor.api import calcular_estado
from motor.datos import cargar
from tests.test_modo_demo import ClienteTrampa
from ui.selector import perfil_demo

RAIZ = Path(__file__).resolve().parents[1]
SUPUESTOS = json.loads((RAIZ / "data" / "processed" / "supuestos.json").read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def entorno_limpio(monkeypatch, tmp_path):
    """Caché temporal vacío, sin efecto de escritura y con MODO_DEMO apagado: así se prueba el camino con IA."""
    monkeypatch.setattr("config.RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setattr("config.PAUSA_ESCRITURA_SEG", 0)
    monkeypatch.delenv("MODO_DEMO", raising=False)


@pytest.fixture(scope="module")
def estado():
    """estado("COMPAÑIA 29", {"aguinaldo_op": 15}) -> el estado real del motor."""
    empresas = cargar()

    def calcular(empresa, palancas):
        perfil = perfil_demo(empresas, empresa)
        ultima = list(palancas)[-1]
        cambio = {"palanca": ultima, "de": perfil["palancas"][ultima], "a": palancas[ultima]}
        return calcular_estado(empresas, perfil, dict(palancas), cambio, SUPUESTOS)

    return calcular


# --- No hay con quién comparar ---

def test_se_detecta_cuando_no_queda_resto(estado):
    assert sin_comparacion(estado("COMPAÑIA 29", {"aguinaldo_op": 15})) is True
    assert sin_comparacion(estado("COMPAÑIA 36", {"aguinaldo_op": 20})) is False  # el guion
    assert sin_comparacion(estado("COMPAÑIA 36", {"vales_op": 0.06})) is False  # resto de 2: sí hay


def test_la_plantilla_dice_la_razon_real_y_cumple_las_reglas(estado):
    e = estado("COMPAÑIA 29", {"aguinaldo_op": 15})
    texto = plantilla(e)
    assert texto != TEXTO_EMERGENCIA
    assert texto.startswith(f"Las {e['grupo']['n']} empresas con dato ya tienen el aguinaldo a 15 días o más")
    assert "no queda un grupo con el cual comparar" in texto
    assert es_valido(texto, e)  # ninguna cifra inventada
    assert revisar(texto, e) == []  # mismas reglas que los textos de la IA


def test_explicar_no_llama_a_la_ia_y_no_muestra_el_texto_de_emergencia(estado):
    e = estado("COMPAÑIA 29", {"aguinaldo_op": 15})
    texto = "".join(explicar(e, None, cliente=ClienteTrampa()))  # si llamara a la API, falla
    assert texto == plantilla(e)
    assert e["explicacion"]["fuente"] == "plantilla"


def test_pasa_igual_con_varias_palancas_y_otras_empresas(estado):
    for empresa, palancas in [
        ("COMPAÑIA 29", {"aguinaldo_op": 15, "prima_vac_op": 0.25}),
        ("COMPAÑIA 15", {"aguinaldo_op": 15}),
        ("COMPAÑIA 15", {"prima_vac_op": 0.25}),
    ]:
        e = estado(empresa, palancas)
        if not sin_comparacion(e):
            continue
        texto = plantilla(e)
        assert texto != TEXTO_EMERGENCIA and es_valido(texto, e) and revisar(texto, e) == [], (empresa, texto)


# --- En la app completa ---

def _clic(at, clave, veces=1):
    for _ in range(veces):
        next(b for b in at.button if b.key == clave).click().run()


def test_en_la_app_bajar_al_minimo_explica_la_razon(monkeypatch):
    monkeypatch.setenv("MODO_DEMO", "1")
    at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=90).run()
    selector = at.selectbox[0]
    selector.select(next(o for o in selector.options if "COMPAÑIA 29" in o)).run()
    _clic(at, "menos_aguinaldo_op", 12)  # de 26 a 15 días, el mínimo
    assert not at.exception
    _clic(at, "btn_explicar")
    assert not at.exception
    explicado = at.session_state["estado_explicado"]
    assert explicado["explicacion"]["texto"] != TEXTO_EMERGENCIA
    assert "no queda un grupo con el cual comparar" in explicado["explicacion"]["texto"]
