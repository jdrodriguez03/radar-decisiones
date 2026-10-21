"""Distribución de la pantalla final (integración). Dueño: Gaby."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def app_con_aguinaldo_a_20():
    at = AppTest.from_file(APP, default_timeout=60).run()
    for _ in range(5):
        next(b for b in at.button if b.key == "mas_aguinaldo_op").click().run()
    return at


def textos(at):
    return " ".join(m.value for m in at.markdown)


def test_ya_no_esta_la_grafica_por_palanca():
    at = app_con_aguinaldo_a_20()
    assert not at.exception
    assert not [b for b in at.button if b.key == "btn_palanca"]


def test_la_tabla_usa_los_titulos_nuevos():
    at = app_con_aguinaldo_a_20()
    html = textos(at)
    for titulo in ("Situación actual", "Empresas con las medidas", "Empresas sin las medidas"):
        assert f"<th>{titulo}</th>" in html
    assert "<th>Grupo</th>" not in html and "<th>Resto</th>" not in html


def test_supuestos_con_titulo_en_la_columna_central():
    at = app_con_aguinaldo_a_20()
    assert "Modificación de supuestos" in textos(at)
    assert at.number_input(key="d_supuestos_baja").value > 0  # el panel ⚙ sigue funcionando


def test_cambiar_el_costo_por_baja_cambia_la_brecha():
    at = app_con_aguinaldo_a_20()
    antes = [m.value for m in at.markdown if 'class="peso"' in m.value]
    at.number_input(key="d_supuestos_baja").set_value(30000).run()
    assert not at.exception
    assert [m.value for m in at.markdown if 'class="peso"' in m.value] != antes


def test_la_grafica_dice_con_y_sin_la_medida():
    from ui import comparativo

    at = app_con_aguinaldo_a_20()
    assert not at.exception
    fuente = Path(comparativo.__file__).read_text(encoding="utf-8")
    assert 'f"Con la medida (' in fuente and 'f"Sin la medida (' in fuente
    assert 'f"Grupo (' not in fuente and 'f"Resto (' not in fuente


def test_un_costo_negativo_se_muestra_como_ahorro():
    at = AppTest.from_file(APP, default_timeout=60).run()
    next(b for b in at.button if b.key == "menos_sal_dia_ini").click().run()  # bajar el salario: la medida ahorra
    assert not at.exception
    pesos = [m.value for m in at.markdown if 'class="peso"' in m.value]
    medida = next(p for p in pesos if "Costo Anual de la Medida" in p)
    assert '<div class="peso-ahorro">Ahorro</div>' in medida
    assert "$5.248.700" in medida and "$-" not in medida


def test_sin_costos_negativos_no_aparece_ahorro():
    at = app_con_aguinaldo_a_20()
    assert not any("Ahorro" in m.value for m in at.markdown if 'class="peso"' in m.value)
