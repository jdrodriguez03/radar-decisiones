"""Sandbox de Juanes: panel ⚙ y etiquetas de procedencia con el fixture 01.

Correr desde la raíz del repo:  streamlit run sandbox/d_soporte.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para poder importar config, motor y ui

import streamlit as st

from config import RUTA_FIXTURES
from motor.pesos import costo_brecha, costo_medida
from ui import supuestos
from ui.procedencia import calculado, observado, supuesto

st.set_page_config(page_title="Sandbox D · ⚙ y etiquetas")
st.title("Sandbox D · ⚙ y etiquetas")

estado = json.loads((RUTA_FIXTURES / "01_aguinaldo.json").read_text(encoding="utf-8"))
empresa = estado["empresa"]
grupo = estado["grupo"]

sup = supuestos.render()

medida = costo_medida(empresa, estado["palancas_movidas"], sup)
brecha = costo_brecha(
    empresa["indicadores"]["rot_anual"],
    grupo["indicadores"]["rot_anual"],
    empresa["plantilla_op"],
    sup["costo_por_baja"],
)


def millones(pesos):
    return f"${pesos / 1_000_000:.1f} M"


n_grupo = observado(f"{grupo['n']} empresas")
rot_grupo = observado(f"{grupo['indicadores']['rot_anual']:.0%}")
costo_baja = supuesto(f"${sup['costo_por_baja']:,.0f}")

st.markdown(f"Grupo de comparación: {n_grupo} que rotan {rot_grupo} al año", unsafe_allow_html=True)
st.markdown(f"Costo de la medida: {calculado(millones(medida))} al año", unsafe_allow_html=True)
st.markdown(f"Costo de rotar más que el grupo: {calculado(millones(brecha))} al año", unsafe_allow_html=True)
st.markdown(f"Costo por baja usado: {costo_baja}", unsafe_allow_html=True)