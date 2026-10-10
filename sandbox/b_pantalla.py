import json
import sys
from pathlib import Path

import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))  

from ui import comparativo
from ui.controles import render
from ui.tema import aplicar_estilos

CARPETA_FIXTURES = RAIZ / "contrato" / "fixtures"

def _cargar(prefijo):
    """Busca contrato/fixtures/<prefijo>_*.json"""
    archivos = sorted(CARPETA_FIXTURES.glob(f"{prefijo}_*.json"))
    if not archivos:
        st.error(f"No encuentro el fixture {prefijo}_*.json en {CARPETA_FIXTURES}")
        st.stop()
    datos = json.loads(archivos[0].read_text(encoding="utf-8"))
    datos["_archivo"] = archivos[0].name
    return datos

def motor_falso(palancas_movidas):
    """Devuelve el fixture que corresponde a lo que se movió."""
    movidas = set(palancas_movidas)
    if "aguinaldo_op" not in movidas:
        return _cargar("05")                      # nada movido
    if "prima_vac_op" not in movidas:
        return _cargar("01")                      # aguinaldo
    if "sal_dia_ini" not in movidas:
        return _cargar("02")                      # aguinaldo + prima
    return _cargar("03")                          # aguinaldo + prima + salario

st.set_page_config(layout="wide")
aplicar_estilos()

base = _cargar("05")  
col_izq, col_centro = st.columns([1.4, 2.6], gap="large")

with col_izq:
    st.markdown('<div class="titulo-col">Palancas</div>', unsafe_allow_html=True)
    palancas_movidas, cambio = render(base["empresa"])

datos = motor_falso(palancas_movidas)

with col_centro:
    st.markdown('<div class="titulo-col">Comparativo</div>', unsafe_allow_html=True)
    comparativo.render(datos)
    st.caption(f"Fixture en pantalla: {datos['_archivo']}")
    st.caption(f"palancas_movidas: {list(palancas_movidas)}")