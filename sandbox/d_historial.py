"""Sandbox de Juanes: prueba ui/historial.py con los 3 fixtures del guion.

Simula lo que pasará en la demo: el directivo sube el aguinaldo (fixture 01),
después la prima (02) y después el salario (03). Cada clic en "Siguiente paso"
agrega una explicación al historial; la más nueva debe quedar arriba.

Correr desde la raíz del repo:  streamlit run sandbox/d_historial.py
Listo cuando: se ven los tres pasos del guion en orden.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para importar config, ia y ui

import streamlit as st

import config
from ia.plantilla import plantilla
from ui import historial

PASOS = ["01_aguinaldo.json", "02_prima.json", "03_salario.json"]


def cargar_paso(archivo):
    """Lee un fixture. Si no trae explicación (el 02 y el 03 la perdieron al
    regenerarse con el motor real, día 7), se rellena con la plantilla de Julian,
    que es justo lo que haría la app sin internet."""
    estado = json.loads((config.RUTA_FIXTURES / archivo).read_text(encoding="utf-8"))
    if not estado.get("explicacion"):
        estado["explicacion"] = {"fuente": "plantilla", "texto": plantilla(estado)}
    return estado


st.set_page_config(page_title="Sandbox · historial", layout="wide")
st.title("Sandbox · historial de explicaciones")

# session_state guarda datos entre recargas: sin esto, cada clic empezaría de cero.
if "paso" not in st.session_state:
    st.session_state.paso = 0          # cuántos pasos del guion ya se aplicaron
    st.session_state.historial = []

col_botones, col_historial = st.columns([1, 2])

with col_botones:
    st.subheader("Simular la demo")
    hay_mas = st.session_state.paso < len(PASOS)
    if st.button("Siguiente paso", type="primary", disabled=not hay_mas):
        estado = cargar_paso(PASOS[st.session_state.paso])
        st.session_state.historial = historial.agregar(st.session_state.historial, estado)
        st.session_state.paso += 1
    if st.button("Repetir el último paso (no debe duplicarse)", disabled=st.session_state.paso == 0):
        estado = cargar_paso(PASOS[st.session_state.paso - 1])
        st.session_state.historial = historial.agregar(st.session_state.historial, estado)
    if st.button("Restablecer"):
        st.session_state.paso = 0
        st.session_state.historial = []
    st.caption(f"Pasos aplicados: {st.session_state.paso} de {len(PASOS)}")

with col_historial:
    historial.render(st.session_state.historial)
    with st.expander("Ver la lista cruda (lo que guarda session_state)"):
        st.json(st.session_state.historial)