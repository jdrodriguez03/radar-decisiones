"""Pruebas del historial (ui/historial.py). Dueño: Juanes.

Solo prueban la lógica (qué se guarda y en qué orden), no el dibujo: eso se revisa
a ojo en sandbox/d_historial.py.

Cómo se corre (desde la raíz del repositorio):
    pytest tests/test_historial.py -v
"""
import json

import pytest

import config
from ui.historial import agregar, describir_cambio, nueva_entrada

PASOS = ["01_aguinaldo.json", "02_prima.json", "03_salario.json"]


def fixture(nombre, texto="Texto de prueba."):
    """Lee un fixture real y le pone una explicación si no trae (el 02 y el 03 no traen)."""
    estado = json.loads((config.RUTA_FIXTURES / nombre).read_text(encoding="utf-8"))
    estado.setdefault("explicacion", {"fuente": "plantilla", "texto": texto})
    return estado


@pytest.mark.parametrize(
    "cambio, esperado",
    [
        ({"palanca": "aguinaldo_op", "de": 15, "a": 20}, "aguinaldo 15 → 20 días"),
        ({"palanca": "prima_vac_op", "de": 0.25, "a": 0.5}, "prima vacacional 25% → 50%"),
        ({"palanca": "sal_dia_ini", "de": 323.61, "a": 350}, "salario inicial $324 → $350"),
        ({"palanca": "vales_op", "de": 0.09, "a": 0.12}, "vales 9% → 12%"),
        ({"palanca": "rutas_x100", "de": 2.85, "a": 3}, "rutas 2.85 → 3 por cada 100"),
        (None, "situación inicial"),
    ],
)
def test_describir_cambio(cambio, esperado):
    assert describir_cambio(cambio) == esperado


def test_los_tres_pasos_del_guion_en_orden():
    """El 'Listo cuando' del día 9: los tres pasos quedan guardados en el orden en que pasaron."""
    historial = []
    for nombre in PASOS:
        historial = agregar(historial, fixture(nombre))
    assert [e["cambio"] for e in historial] == [
        "aguinaldo 15 → 20 días",
        "prima vacacional 25% → 50%",
        "salario inicial $324 → $350",
    ]
    assert [e["n"] for e in historial] == [22, 16, 5]
    assert [e["senal"] for e in historial] == ["clara", "débil", "no concluyente"]


def test_estado_inicial_no_se_guarda():
    assert nueva_entrada(fixture("05_inicial.json")) is None
    assert agregar([], fixture("05_inicial.json")) == []


def test_sin_explicacion_no_se_guarda():
    estado = fixture("01_aguinaldo.json")
    estado.pop("explicacion")
    assert agregar([], estado) == []


def test_mismo_estado_dos_veces_no_se_duplica():
    """Streamlit recarga la página seguido; el mismo estado no debe aparecer dos veces."""
    estado = fixture("01_aguinaldo.json")
    historial = agregar(agregar([], estado), estado)
    assert len(historial) == 1


def test_no_modifica_la_lista_original():
    original = []
    agregar(original, fixture("01_aguinaldo.json"))
    assert original == []


def test_cambiar_de_empresa_empieza_de_cero():
    historial = agregar([], fixture("01_aguinaldo.json"))      # COMPAÑIA 36
    historial = agregar(historial, fixture("04_ya_rota_menos.json"))  # COMPAÑIA 37
    assert [e["empresa"] for e in historial] == ["COMPAÑIA 37"]


def test_maximo_de_entradas():
    """Con maximo=2, al llegar el tercer paso se descarta el más viejo."""
    historial = []
    for nombre in PASOS:
        historial = agregar(historial, fixture(nombre), maximo=2)
    assert [e["n"] for e in historial] == [16, 5]