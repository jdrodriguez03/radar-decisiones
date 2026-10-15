"""Pruebas de ia/reglas.py: cada regla atrapa lo que debe y deja pasar lo que debe."""
import json

import pytest

from config import RUTA_FIXTURES
from ia.reglas import fallas_graves, menciona_n, oraciones, revisar


def cargar(nombre):
    return json.loads((RUTA_FIXTURES / f"{nombre}.json").read_text(encoding="utf-8"))


# Texto del paso 03 con el aviso fijo (decisión T3-D2): debe pasar todas las reglas.
BUENO_03 = (
    "Con el salario inicial de $350 diarios, la prima vacacional de 50% y el aguinaldo de 20 días, "
    "quedan 5 empresas, antes 16; pierden 12% de su plantilla al año y las demás, 38%. "
    "Para su empresa, la diferencia equivale a $8.5 millones de pesos al año en bajas, "
    "contra $17.6 millones de la medida. "
    "Con estos datos la señal no es concluyente: tómelo como referencia, no como conclusión."
)


def test_texto_bueno_pasa_todas_las_reglas():
    assert revisar(BUENO_03, cargar("03_salario")) == []


def test_el_punto_decimal_no_corta_la_oracion():
    assert len(oraciones("Equivale a $6.3 millones al año. Además, la mayoría da prima.")) == 2


def test_el_punto_y_coma_no_corta_la_oracion():
    assert len(oraciones("Pierden 22% al año; las demás, 53%.")) == 1


@pytest.mark.parametrize("texto, esperado", [
    ("Las 22 empresas que ya dan", True),
    ("quedan 16 empresas, antes 22", False),  # el 22 es el anterior, no el n
    ("22 de las 38 empresas comparables", True),
    ("pierden 22% de su plantilla", False),  # el 22% no cuenta como n
    ("las 122 empresas", False),
])
def test_menciona_n(texto, esperado):
    assert menciona_n(texto, 22) is esperado


@pytest.mark.parametrize("palabra", ["reducirá", "Reduce", "logrará", "bajará", "hará que", "garantiza", "ahorrará"])
def test_palabras_de_causa_son_graves(palabra):
    texto = f"Las 22 empresas muestran que esto {palabra} las bajas."
    assert fallas_graves(texto, cargar("01_aguinaldo"))


def test_jerga_falla_en_pruebas_pero_no_es_grave():
    texto = "Las 22 empresas tienen menor rotación."
    estado = cargar("01_aguinaldo")
    assert fallas_graves(texto, estado) == []
    assert "usa «rotación»" in revisar(texto, estado)


def test_sin_advertencia_en_no_concluyente_es_grave():
    sin_aviso = BUENO_03.replace("Con estos datos la señal no es concluyente: tómelo como referencia, no como conclusión.", "Todo bien.")
    assert fallas_graves(sin_aviso, cargar("03_salario"))


def test_cuatro_oraciones_y_texto_largo_fallan():
    fallas = revisar("Las 22 empresas. Uno. Dos. " + "palabra " * 80 + "fin.", cargar("01_aguinaldo"))
    assert any("oraciones" in f for f in fallas)
    assert any("palabras" in f for f in fallas)


@pytest.mark.parametrize("frase, prohibida", [
    ("así que conviene leerlo con cautela", "así que"),
    ("Con tan pocas empresas no es concluyente", "tan pocas"),
    ("Con solo 20 empresas no es concluyente", "con solo"),
])
def test_no_explica_por_que_la_senal_es_debil(frase, prohibida):
    assert f"usa «{prohibida}»" in revisar(f"Las 22 empresas pierden 22%. {frase}.", cargar("01_aguinaldo"))


def test_numero_pegado_falla_y_limpiar_lo_arregla():
    from ia.reglas import limpiar

    texto = "Las 22 empresas: contra $14.4millones de la medida."
    assert "tiene un número pegado a una palabra" in revisar(texto, cargar("01_aguinaldo"))
    assert limpiar(texto) == "Las 22 empresas: contra $14.4 millones de la medida."
    assert limpiar("$6.3 millones, 22% y 1,438") == "$6.3 millones, 22% y 1,438"  # lo correcto no se toca
