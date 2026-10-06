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
from ia.prompts import PROMPT_SISTEMA, armar_mensaje

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
    st.subheader(f"Respuesta de {config.MODELO_IA}")
    if st.button("Generar explicación", type="primary"):
        try:
            cliente = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            inicio = time.perf_counter()
            respuesta = cliente.messages.create(
                model=config.MODELO_IA,
                max_tokens=300,
                system=PROMPT_SISTEMA,
                messages=[{"role": "user", "content": armar_mensaje(estado, anterior)}],
            )
            segundos = time.perf_counter() - inicio
            st.write(respuesta.content[0].text)
            st.caption(
                f"{segundos:.1f} s · {respuesta.usage.input_tokens} tokens de entrada · "
                f"{respuesta.usage.output_tokens} de salida"
            )
        except (anthropic.APIError, KeyError, FileNotFoundError) as error:  # error de la API o llave no encontrada
            st.error(f"{type(error).__name__}: {error}")
