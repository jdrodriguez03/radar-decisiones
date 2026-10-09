import json

from config import RUTA_EJEMPLO, RUTA_FIXTURES
from ia.plantilla import fmt_pct, fmt_pesos, plantilla


def cargar_ejemplo():
    return json.loads(RUTA_EJEMPLO.read_text(encoding="utf-8"))


def test_plantilla_con_el_ejemplo():
    texto = plantilla(cargar_ejemplo())
    assert "22 empresas" in texto
    assert "22%" in texto
    assert "53%" in texto


def test_formatos():
    assert fmt_pct(0.222) == "22%"
    assert fmt_pesos(6341580) == "$6.3 millones"


def test_brecha_en_cero():
    estado = cargar_ejemplo()
    estado["pesos"]["costo_brecha_anual"] = 0
    assert "ya rota menos" in plantilla(estado)


def test_estado_inicial_sin_cambio():
    estado = json.loads((RUTA_FIXTURES / "05_inicial.json").read_text(encoding="utf-8"))
    texto = plantilla(estado)  # antes se rompía: cambio es None
    assert "52%" in texto  # lo que pierde hoy la empresa
    assert "39 empresas" in texto
    assert "36%" in texto