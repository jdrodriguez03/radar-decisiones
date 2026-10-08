"""Sandbox de Julian: prueba la explicación de la IA con contrato/ejemplo.json.

Correr desde la raíz del repo:  streamlit run sandbox/c_explicacion.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para poder importar config e ia

import anthropic
import streamlit as st

import config
from ia.plantilla import plantilla
from ia.prompts import PROMPT_SISTEMA, armar_mensaje


def stream_api(estado, anterior):
    """Llama a la API en streaming y devuelve trozos de texto."""
    cliente = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    with cliente.messages.stream(
        model=config.MODELO_IA,
        max_tokens=300,
        system=PROMPT_SISTEMA,
        messages=[{"role": "user", "content": armar_mensaje(estado, anterior)}],
    ) as flujo:
        yield from flujo.text_stream


def stream_simulado(estado, pausa=0.04):
    """Escribe la plantilla palabra por palabra, sin API."""
    for palabra in plantilla(estado).split(" "):
        yield palabra + " "
        time.sleep(pausa)


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
    modo = st.radio("Fuente del texto", ["API real", "Simulado (plantilla)"], horizontal=True)
    st.subheader(f"Respuesta de {config.MODELO_IA}" if modo == "API real" else "Respuesta simulada")
    if st.button("Generar explicación", type="primary"):
        generador = stream_api(estado, anterior) if modo == "API real" else stream_simulado(estado)
        tiempos = {}
        try:
            st.write_stream(sin_latex(con_tiempos(generador, tiempos)))
            m1, m2 = st.columns(2)
            m1.metric("Primera palabra", f"{tiempos.get('primera', 0):.2f} s")
            m2.metric("Texto completo", f"{tiempos.get('total', 0):.2f} s")
        except (anthropic.APIError, KeyError, FileNotFoundError) as error:  # error de la API o llave no encontrada
            st.error(f"{type(error).__name__}: {error}")

