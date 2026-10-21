import json
import re

import pytest

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
    assert "ya pierde igual o menos gente" in plantilla(estado)


def test_estado_inicial_sin_cambio():
    estado = json.loads((RUTA_FIXTURES / "05_inicial.json").read_text(encoding="utf-8"))
    texto = plantilla(estado)  # antes se rompía: cambio es None
    assert "52%" in texto  # lo que pierde hoy la empresa
    assert "39 empresas" in texto
    assert "36%" in texto


# --- La plantilla habla igual que el prompt: es lo que ve el público cuando la IA falla ---

PROHIBIDAS = ["logrará", "reducirá", "reduce", "disminuye", "promedio", "pasaría a", "obtendrá",
              "grupo de comparación", "brecha", "rotación", "rotar", "sector"]


@pytest.mark.parametrize("fixture", sorted(p.stem for p in RUTA_FIXTURES.glob("*.json")))
def test_cumple_las_reglas_del_prompt(fixture):
    texto = plantilla(json.loads((RUTA_FIXTURES / f"{fixture}.json").read_text(encoding="utf-8")))
    oraciones = [o for o in re.split(r"(?<=[.!?])\s+", texto) if o]
    assert len(oraciones) <= 3
    assert len(texto.split()) <= 75
    assert not [p for p in PROHIBIDAS if p in texto.lower()]


def test_nombra_todas_las_palancas_movidas():
    texto = plantilla(json.loads((RUTA_FIXTURES / "03_salario.json").read_text(encoding="utf-8")))
    assert "aguinaldo" in texto and "prima vacacional" in texto and "salario inicial" in texto


def test_avisa_si_el_grupo_se_completo():
    estado = json.loads((RUTA_FIXTURES / "03_salario.json").read_text(encoding="utf-8"))
    estado["grupo"]["completado"] = True
    assert "se completó con empresas parecidas" in plantilla(estado)


def test_estado_inicial_dice_el_problema_en_personas():
    texto = plantilla(json.loads((RUTA_FIXTURES / "05_inicial.json").read_text(encoding="utf-8")))
    assert "742 personas" in texto and "297" in texto



def test_un_costo_negativo_se_escribe_como_ahorro_sin_signo():
    """Al bajar una prestación la medida ahorra: la plantilla no debe escribir «$-2.5 millones»."""
    import copy

    from ia.reglas import fallas_graves
    from ia.validador import cifras_inventadas

    base = json.loads(RUTA_EJEMPLO.read_text(encoding="utf-8"))
    for brecha in (6_000_000, 0):
        estado = copy.deepcopy(base)
        estado["pesos"]["costo_medida_anual"] = -2_547_798
        estado["pesos"]["costo_brecha_anual"] = brecha
        texto = plantilla(estado)
        assert "$-" not in texto and "-$" not in texto
        assert "representa un ahorro de $2.5 millones de pesos al año" in texto
        assert "costaría" not in texto
        assert cifras_inventadas(texto, estado) == []
        assert not fallas_graves(texto, estado)
