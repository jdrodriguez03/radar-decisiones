import json

from streamlit.testing.v1 import AppTest

from config import RUTA_FIXTURES
from ui.explicacion import pie, sin_latex


def cargar_fixture(nombre):
    return json.loads((RUTA_FIXTURES / f"{nombre}.json").read_text(encoding="utf-8"))


def test_pie_con_senal_y_n():
    assert pie(cargar_fixture("01_aguinaldo")) == "Señal clara · 22 empresas que ya lo hacen"


def test_pie_avisa_si_el_grupo_se_completo():
    estado = cargar_fixture("03_salario")
    estado["grupo"]["completado"] = True
    assert pie(estado).endswith("grupo completado con empresas similares")


def test_pie_en_el_estado_inicial():
    assert pie(cargar_fixture("05_inicial")) == "Comparado con las 39 empresas de la encuesta"


def test_los_pesos_no_se_vuelven_formula():
    assert sin_latex("$6.3 millones contra $2.3 millones") == r"\$6.3 millones contra \$2.3 millones"


def _app_con_cache():
    """Mini app que dibuja el panel con el fixture 01 y un caché temporal con su texto."""
    import json
    import tempfile
    from pathlib import Path

    import streamlit as st

    import config
    from ia.cache import guardar, llave
    from ui.explicacion import render

    estado = json.loads((config.RUTA_FIXTURES / "01_aguinaldo.json").read_text(encoding="utf-8"))
    config.RUTA_CACHE = Path(tempfile.mkdtemp()) / "cache.json"
    guardar({llave(estado): {"texto": "Las 22 empresas pierden 22% al año; las demás, 53%. Equivale a $6.3 millones."}})
    render(st.container(), estado, None)


def test_render_dibuja_el_texto_y_el_pie():
    app = AppTest.from_function(_app_con_cache).run(timeout=10)
    assert not app.exception
    assert "Las 22 empresas pierden 22%" in app.markdown[0].value
    assert r"\$6.3 millones" in app.markdown[0].value  # el $ quedó escapado
    assert app.caption[0].value == "Señal clara · 22 empresas que ya lo hacen"
