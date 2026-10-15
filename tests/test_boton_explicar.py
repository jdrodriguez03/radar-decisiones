"""Pruebas del botón Explicar: el "anterior" es la última combinación explicada, no el último clic."""
import copy
import json

from streamlit.testing.v1 import AppTest

from config import RUTA_FIXTURES
from ia.prompts import armar_mensaje, cambios_desde
from ui.explicacion import AVISO_PENDIENTE, falta_explicar


def cargar(nombre):
    return json.loads((RUTA_FIXTURES / f"{nombre}.json").read_text(encoding="utf-8"))


def bloque_cambios(mensaje):
    """Solo la parte del mensaje que dice qué palancas cambiaron (antes del JSON)."""
    return mensaje.split("Resultado actual")[0]


# --- El mensaje a la IA ---

def test_dos_palancas_sin_explicar_en_medio_nombra_las_dos():
    # Se explicó el aguinaldo (01); luego se movieron prima y salario sin pulsar Explicar (03).
    cambios = bloque_cambios(armar_mensaje(cargar("03_salario"), cargar("01_aguinaldo")))
    assert "prima vacacional de 50% (nueva)" in cambios
    assert "salario inicial de $350 (nueva)" in cambios
    assert "Ya tenía: aguinaldo de 20 días" in cambios


def test_no_manda_el_valor_anterior_de_la_palanca():
    cambios = bloque_cambios(armar_mensaje(cargar("03_salario"), cargar("01_aguinaldo")))
    assert "25%" not in cambios  # la prima de antes ya se ve en pantalla (decisión D3a)
    assert "324" not in cambios


def test_palanca_quitada_se_dice():
    # Se explicó aguinaldo + prima (02); luego la prima volvió a su valor real (01).
    cambios = bloque_cambios(armar_mensaje(cargar("01_aguinaldo"), cargar("02_prima")))
    assert "quitó prima vacacional" in cambios


def test_primera_comparacion_compara_contra_valores_reales():
    cambios = bloque_cambios(armar_mensaje(cargar("02_prima"), None))
    assert "frente a sus valores reales" in cambios
    assert "aguinaldo de 20 días (nueva)" in cambios
    assert "prima vacacional de 50% (nueva)" in cambios


def test_el_ultimo_clic_no_va_en_el_json():
    # Con varios cambios, "cambio" (solo el último clic) contradiría la lista de cambios.
    mensaje = armar_mensaje(cargar("03_salario"), cargar("01_aguinaldo"))
    assert '"cambio"' not in mensaje


def test_misma_combinacion_dos_veces():
    cambios, ya_tenia = cambios_desde(cargar("02_prima"), cargar("02_prima"))
    assert cambios == []
    assert set(ya_tenia) == {"aguinaldo_op", "prima_vac_op"}


def test_cambiar_el_nivel_de_una_palanca_que_ya_estaba():
    antes, ahora = cargar("01_aguinaldo"), cargar("01_aguinaldo")
    ahora["palancas_movidas"]["aguinaldo_op"] = 25
    cambios, _ = cambios_desde(ahora, antes)
    assert cambios == [{"palanca": "aguinaldo_op", "de": 20, "a": 25, "tipo": "cambiada"}]


# --- Cuándo falta pulsar Explicar ---

def test_falta_explicar():
    explicado = cargar("01_aguinaldo")
    assert falta_explicar(explicado, None)  # aún no se pulsa
    assert not falta_explicar(copy.deepcopy(explicado), explicado)  # nada cambió
    assert falta_explicar(cargar("02_prima"), explicado)  # se movió una palanca
    otro_costo = copy.deepcopy(explicado)
    otro_costo["pesos"]["supuestos"]["costo_por_baja"] = 30000
    assert falta_explicar(otro_costo, explicado)  # se cambió el costo por baja en el ⚙


# --- Lo que se ve en el panel ---

def _panel(modo):
    import json

    import streamlit as st

    from config import RUTA_FIXTURES
    from ui.explicacion import aviso_pendiente, mostrar

    estado = json.loads((RUTA_FIXTURES / "01_aguinaldo.json").read_text(encoding="utf-8"))
    estado["explicacion"] = {"fuente": "llm", "texto": "Las 22 empresas que ya dan aguinaldo de 20 días."}
    contenedor = st.container()
    if modo == "pendiente":
        aviso_pendiente(contenedor)
    else:
        mostrar(contenedor, estado)


def test_aviso_pendiente_oculta_el_texto_viejo():
    app = AppTest.from_function(_panel, args=("pendiente",)).run()
    assert app.info[0].value == AVISO_PENDIENTE
    assert not any("22 empresas" in m.value for m in app.markdown)


def test_mostrar_redibuja_sin_llamar_a_la_ia():
    app = AppTest.from_function(_panel, args=("mostrar",)).run()
    assert not app.exception
    assert any("22 empresas" in m.value for m in app.markdown)
    assert app.caption[0].value == "Señal clara · 22 empresas que ya lo hacen"
