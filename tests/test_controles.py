"""Palancas con los valores reales de las 40 empresas demo. Dueño: Gaby.

Algunas empresas traen valores con muchos decimales o fuera del rango de la encuesta
(rutas de la COMPAÑIA 1: 10.4895104895105, con máximo 10.8 y paso 0.5). El slider debe dibujarse
igual, sin el error de Streamlit «value is greater than the max_value».
"""
import math
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from motor.datos import cargar
from ui.controles import CONTROLES, _rango
from ui.selector import ids_ordenados, perfil_demo

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

EMPRESAS = cargar()
IDS = ids_ordenados(EMPRESAS)


@pytest.mark.parametrize("empresa_id", IDS)
def test_el_rango_del_slider_contiene_el_valor_real(empresa_id):
    perfil = perfil_demo(EMPRESAS, empresa_id)
    for clave, cfg in CONTROLES.items():
        valor = perfil["palancas"].get(clave)
        if valor is None or math.isnan(valor):  # sin dato: no se dibuja slider
            continue
        real = round(float(valor), 6)  # igual que controles._iniciar
        lo, hi = _rango(cfg, real)
        assert lo <= real <= hi, f"{empresa_id} · {clave}: {real} fuera de [{lo}, {hi}]"
        assert lo < hi


@pytest.mark.parametrize("empresa_id", ["COMPAÑIA 1", "COMPAÑIA 15", "COMPAÑIA 37"])
def test_empresas_con_rutas_de_muchos_decimales_abren_sin_error(empresa_id):
    at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=60).run()
    at.selectbox[0].select(empresa_id).run()
    assert not at.exception, at.exception[0].value if at.exception else ""
    slider = next(s for s in at.slider if s.key == "valor_rutas_x100")
    inicial = slider.value
    # Si ya está en el tope (COMPAÑIA 1) primero baja; si está en el piso (15 y 37) primero sube.
    orden = ("menos", "mas") if inicial >= slider.max else ("mas", "menos")
    for boton in orden:
        next(b for b in at.button if b.key == f"{boton}_rutas_x100").click().run()
        assert not at.exception
    assert next(s.value for s in at.slider if s.key == "valor_rutas_x100") == pytest.approx(inicial)


def test_las_40_empresas_abren_sin_error():
    at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=60).run()
    for empresa_id in IDS:
        at.selectbox[0].select(empresa_id).run()
        assert not at.exception, f"{empresa_id}: {at.exception[0].value}"


def test_si_el_slider_falla_solo_se_ve_el_aviso(monkeypatch):
    """Red de seguridad: si Streamlit no puede dibujar un slider, no sale su error, solo el aviso de rango."""
    from ui import controles

    original = controles._rango

    def rango_roto(cfg, real):  # límites que dejan el valor real por encima del máximo, como el error original
        lo, _ = original(cfg, real)
        return lo - cfg["paso"], real - cfg["paso"] / 10

    monkeypatch.setattr(controles, "_rango", rango_roto)
    at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=60).run()
    assert not at.exception
    assert any("fuera del rango de la encuesta" in m.value for m in at.markdown)
    next(b for b in at.button if b.key == "menos_aguinaldo_op").click().run()  # los botones siguen respondiendo
    assert not at.exception
