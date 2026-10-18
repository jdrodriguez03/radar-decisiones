"""Pruebas del semáforo de evidencia con estados reales del motor. Dueño: Julian."""
import json

import pytest

from config import RUTA_FIXTURES
from ia.semaforo import direccion, lectura_pesos, solidez
from motor.datos import cargar
from scripts.generar_cache import cargar_casos, estado_de
from ui.explicacion import (
    ROJO_ALERTA,
    html_direccion,
    html_pesos,
    html_semaforo,
    html_solidez,
)

SUPUESTOS = {"costo_por_baja": 15000, "costo_ruta_mensual": 35000}


@pytest.fixture(scope="module")
def estado():
    """estado("G1") -> el estado real de ese caso de combinaciones.yaml."""
    empresas, casos = cargar(), cargar_casos()
    return lambda caso: estado_de({"caso": caso}, casos, empresas, SUPUESTOS)


def fixture(nombre):
    return json.loads((RUTA_FIXTURES / f"{nombre}.json").read_text(encoding="utf-8"))


# --- Apartado 1: dirección ---

def test_en_el_guion_rotan_menos(estado):
    for caso in ("G1", "G2", "G3"):
        assert direccion(estado(caso))["rotan_mas"] is False
    assert direccion(estado("G1")) == {
        "rotan_mas": False,
        "titulo": "↓ Rotan menos",
        "detalle": "22 empresas que lo hacen: 22% al año contra 53% del resto",
    }


@pytest.mark.parametrize("caso", ["E1", "E4", "R15-2"])
def test_si_el_grupo_rota_mas_sale_la_alerta(estado, caso):
    dir_ = direccion(estado(caso))
    assert dir_["rotan_mas"] is True
    assert dir_["titulo"] == "⚠ Rotan más"


def test_si_rotan_igual_tambien_es_alerta(estado):
    empate = estado("G1")
    empate["grupo"]["indicadores"]["rot_anual"] = empate["resto"]["indicadores"]["rot_anual"]
    assert direccion(empate)["rotan_mas"] is True


# --- Apartado 2: solidez ---

def test_el_guion_va_de_verde_a_amarillo_a_naranja(estado):
    assert [solidez(estado(c))["color"] for c in ("G1", "G2", "G3")] == ["verde", "amarillo", "naranja"]


def test_la_solidez_dice_evidencia_no_buena_decision(estado):
    assert solidez(estado("G1"))["etiqueta"] == "Evidencia clara"


def test_la_alerta_roja_y_la_solidez_van_por_separado(estado):
    # E4: rotan más, pero tampoco eso es seguro: la barra lo dice aparte
    assert direccion(estado("E4"))["rotan_mas"] is True
    assert solidez(estado("E4"))["color"] == "naranja"


@pytest.mark.parametrize(("senal", "etiqueta"), [
    ("clara", "Evidencia clara de que rotan más"),
    ("débil", "Evidencia débil de que rotan más"),
    ("no concluyente", "No concluyente"),
])
def test_si_rotan_mas_la_etiqueta_lo_dice(estado, senal, etiqueta):
    # Hoy no existe en los datos un "rotan más" con señal clara o débil; si aparece, el verde no confunde
    rotan_mas = estado("R15-2")  # no completado, el grupo rota más
    rotan_mas["senal"]["etiqueta"] = senal
    assert solidez(rotan_mas)["etiqueta"] == etiqueta


def test_grupo_completado_sale_naranja_y_lo_dice(estado):
    sol = solidez(estado("E3"))
    assert sol["color"] == "naranja"
    assert sol["etiqueta"] == "No concluyente · grupo completado"


def test_completado_con_senal_clara_sigue_naranja(estado):
    completado = estado("G1")
    completado["grupo"]["completado"] = True  # ya no son empresas que de verdad lo hacen
    assert solidez(completado)["color"] == "naranja"


def test_estado_inicial_no_dibuja_nada():
    inicial = fixture("05_inicial")
    assert direccion(inicial) is None
    assert solidez(inicial) is None
    assert lectura_pesos(inicial) is None


# --- La frase de los pesos: lado a lado, nunca dividida ---

def test_pesos_dice_cual_es_mayor(estado):
    assert "cuesta menos" in lectura_pesos(estado("G1"))  # $2.3 M contra $6.3 M
    assert "cuesta más" in lectura_pesos(estado("G3"))  # $17.6 M contra $8.5 M


def test_pesos_con_ahorro(estado):
    assert lectura_pesos(estado("E5")).startswith("La medida ahorra $5.1 M")


def test_pesos_si_ya_rota_menos():
    assert lectura_pesos(fixture("04_ya_rota_menos")) == "Su empresa ya rota menos que esas empresas"


# --- El HTML ---

def test_html_rotan_menos_va_sin_rojo(estado):
    e = estado("G2")
    html = html_semaforo(direccion(e), solidez(e), lectura_pesos(e))
    assert "↓ Rotan menos" in html
    assert "Evidencia débil" in html  # la etiqueta siempre escrita, nunca solo el color
    assert ROJO_ALERTA not in html
    assert html.count("flex:1") == 3  # tres segmentos: naranja, amarillo y verde
    assert "$" not in html and "&#36;3.7 M" in html  # el $ va como &#36; para que no sea fórmula


def test_html_rotan_mas_va_en_rojo(estado):
    e = estado("E4")
    html = html_semaforo(direccion(e), solidez(e), lectura_pesos(e))
    assert "⚠ Rotan más" in html
    assert ROJO_ALERTA in html


def test_las_piezas_se_pueden_dibujar_por_separado(estado):
    e = estado("E4")
    direccion_sola = html_direccion(direccion(e))
    assert "⚠ Rotan más" in direccion_sola and "Solidez" not in direccion_sola
    solidez_sola = html_solidez(solidez(e))
    assert "No concluyente" in solidez_sola and "Rotan" not in solidez_sola
    assert "cuesta más" in html_pesos(lectura_pesos(e))
    # juntas dan exactamente lo mismo que el atajo
    assert html_semaforo(direccion(e), solidez(e), lectura_pesos(e)) == (
        direccion_sola + solidez_sola + html_pesos(lectura_pesos(e))
    )
