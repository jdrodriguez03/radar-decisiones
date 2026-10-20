"""Sandbox del resumen en PDF (crítica 4): elige escenarios y baja el PDF. Dueño: Julian.

Usa los pasos reales del caché, con su explicación, como si el directivo los hubiera guardado:
    streamlit run sandbox/c_resumen.py
"""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para poder importar config, motor, ia y ui

import streamlit as st

import config
from ia.cache import buscar
from ia.resumen import contenido, escenarios_para_resumen
from motor.datos import cargar
from scripts.generar_cache import SECUENCIAS, armar_secuencias, cargar_casos
from ui import explicacion
from ui.tema import aplicar_estilos

st.set_page_config(layout="wide")
aplicar_estilos()
st.title("Resumen para comité (PDF)")


@st.cache_data
def estados():
    supuestos = json.loads(config.RUTA_SUPUESTOS.read_text(encoding="utf-8"))
    casos = cargar_casos()
    secuencias = armar_secuencias(casos, cargar(), supuestos)
    nombres = [p.get("caso", p.get("empresa")) for pasos in SECUENCIAS.values() for p in pasos] + list(casos)
    return list(zip(nombres, [e for s in secuencias for e in s], strict=True))


todos = estados()
empresa = st.selectbox("Empresa", sorted({e["empresa"]["id"] for _, e in todos}))
de_esta = [(nombre, e) for nombre, e in todos if e["empresa"]["id"] == empresa]
elegidos = st.multiselect(
    "Escenarios «guardados» (en el orden en que se eligen)",
    options=range(len(de_esta)),
    format_func=lambda i: f"{de_esta[i][0]} · {de_esta[i][1]['palancas_movidas']}",
)
con_texto = st.toggle("Con explicación (como si se hubiera pulsado Explicar antes de guardar)", value=True)

guardados = [
    {"hora": datetime.now().astimezone().isoformat(timespec="seconds"), "estado": de_esta[i][1],
     "explicacion": buscar(de_esta[i][1]) if con_texto else None}
    for i in elegidos
]
actual = de_esta[elegidos[-1]][1] if elegidos else de_esta[0][1]

explicacion.boton_resumen(st.container(), actual, guardados)

st.subheader("Lo que lleva el PDF")
datos = contenido(escenarios_para_resumen(actual, guardados), datetime.now().astimezone())
st.write(datos["titulo"], "·", datos["subtitulo"])
st.table([dict(datos["situacion"])])
st.table([dict(zip(datos["encabezados"], f["celdas"], strict=True)) for f in datos["filas"]])
