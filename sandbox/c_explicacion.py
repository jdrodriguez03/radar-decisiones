"""Sandbox de Julian: prueba la explicación de la IA con contrato/ejemplo.json.

Correr desde la raíz del repo:  streamlit run sandbox/c_explicacion.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para poder importar config e ia

import streamlit as st

import config
from ia.explicar import explicar
from ia.plantilla import plantilla
from ia.prompts import armar_mensaje


def stream_simulado(estado, pausa=0.04):
    """Escribe la plantilla palabra por palabra, sin API."""
    for palabra in plantilla(estado).split(" "):
        yield palabra + " "
        time.sleep(pausa)


class FlujoLento:
    """Imita una API que tarda 6 s en dar la primera palabra."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    @property
    def text_stream(self):
        time.sleep(6)
        yield "Este texto llega tarde y no debería verse."


class ClienteLento:
    def __init__(self):
        self.messages = self

    def stream(self, **kwargs):
        return FlujoLento()


def con_tiempos(generador, tiempos):
    """Anota cuándo llegó la primera palabra y cuándo terminó el texto."""
    inicio = time.perf_counter()
    for trozo in generador:
        if "primera" not in tiempos:
            tiempos["primera"] = time.perf_counter() - inicio
        yield trozo
    tiempos["total"] = time.perf_counter() - inicio


def sin_latex(generador):
    """Streamlit lee $...$ como fórmula: se escapa cada $ para que se vea como pesos."""
    for trozo in generador:
        yield trozo.replace("$", r"\$")


st.set_page_config(page_title="Sandbox · explicación IA", layout="wide")
st.title("Sandbox · explicación de la IA")

estado = json.loads(config.RUTA_EJEMPLO.read_text(encoding="utf-8"))
anterior = None  # el ejemplo es el primer paso; luego se probarán los fixtures con estado anterior

col_estado, col_ia = st.columns(2)
with col_estado:
    st.subheader("Estado enviado")
    st.caption(f"{estado['empresa']['id']} · {estado['cambio']['palanca']} {estado['cambio']['de']} → {estado['cambio']['a']}")
    with st.expander("Mensaje exacto que recibe la IA"):
        st.code(armar_mensaje(estado, anterior), language="text")

with col_ia:
    modo = st.radio(
        "Fuente del texto",
        ["API real", "API lenta (prueba del límite)", "Simulado (plantilla)"],
        horizontal=True,
    )
    st.subheader(f"Respuesta de {config.MODELO_IA}" if modo == "API real" else "Respuesta")
    if st.button("Generar explicación", type="primary"):
        if modo == "Simulado (plantilla)":
            generador = stream_simulado(estado)
        else:
            cliente = ClienteLento() if modo.startswith("API lenta") else None
            pulso = st.empty()  # marcador invisible: tocarlo deja que Streamlit note un clic nuevo
            generador = explicar(estado, anterior, cliente=cliente, latido=pulso.empty)
        tiempos = {}
        st.write_stream(sin_latex(con_tiempos(generador, tiempos)))
        m1, m2, m3 = st.columns(3)
        m1.metric("Primera palabra", f"{tiempos.get('primera', 0):.2f} s")
        m2.metric("Texto completo", f"{tiempos.get('total', 0):.2f} s")
        m3.metric("Fuente usada", estado["explicacion"]["fuente"] if modo != "Simulado (plantilla)" else "simulado")
