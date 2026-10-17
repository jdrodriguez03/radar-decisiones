"""Sandbox del semáforo de evidencia: los 26 pasos del caché, uno debajo de otro. Dueño: Julian.

Para que Gaby vea cómo se ve antes de conectarlo en app.py:
    streamlit run sandbox/c_semaforo.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para poder importar config, motor, ia y ui

import streamlit as st

import config
from motor.datos import cargar
from scripts.generar_cache import SECUENCIAS, armar_secuencias, cargar_casos
from ui import explicacion
from ui.tema import aplicar_estilos

st.set_page_config(layout="wide")
aplicar_estilos()
st.title("Semáforo de evidencia")


@st.cache_data
def estados():
    supuestos = json.loads(config.RUTA_SUPUESTOS.read_text(encoding="utf-8"))
    casos = cargar_casos()
    secuencias = armar_secuencias(casos, cargar(), supuestos)
    nombres = [p.get("caso", p.get("empresa")) for pasos in SECUENCIAS.values() for p in pasos] + list(casos)
    return list(zip(nombres, [e for s in secuencias for e in s], strict=True))


columnas = st.columns(3)
for i, (nombre, estado) in enumerate(estados()):
    with columnas[i % 3]:
        st.caption(f"{nombre} · {estado['empresa']['id']} · {estado['palancas_movidas']}")
        explicacion.semaforo(st.container(), estado)
