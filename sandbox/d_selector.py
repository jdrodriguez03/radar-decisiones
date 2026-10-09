"""Sandbox de Juanes: prueba el selector de empresa sin el resto de la app.

Correr desde la raíz del repo:  streamlit run sandbox/d_selector.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para poder importar config, motor y ui

import streamlit as st
from pydantic import ValidationError

from contrato.modelo import Empresa
from motor.datos import cargar
from ui import selector

st.set_page_config(page_title="Sandbox D · selector", layout="wide")
st.title("Sandbox D · selector de empresa")


@st.cache_data
def _empresas():
    return cargar()


izq, der = st.columns([1, 1.4])

with izq:
    perfil = selector.render(_empresas())

with der:
    st.subheader("Perfil que devuelve render()")
    if perfil is None:
        st.info("Todavía no hay perfil: envía el formulario de Mi empresa.")
    else:
        st.json(perfil)

        # ¿Cumple el bloque "empresa" del contrato?
        try:
            Empresa.model_validate(perfil)
            st.success("✅ Cumple el modelo Empresa de contrato/modelo.py")
        except ValidationError as e:
            st.error(f"❌ No cumple el modelo Empresa:\n\n{e}")

        # "Listo cuando" del día 3 con COMPAÑIA 36 (valores de contrato/ejemplo.json).
        if perfil["id"] == "COMPAÑIA 36":
            p, ind = perfil["palancas"], perfil["indicadores"]
            revisiones = {
                "plantilla 1,438": perfil["plantilla_op"] == 1438,
                "salario $323.61": abs(p["sal_dia_ini"] - 323.61) < 0.01,
                "aguinaldo 15 días": p["aguinaldo_op"] == 15,
                "prima 25%": abs(p["prima_vac_op"] - 0.25) < 1e-6,
                "rotación anual 51.6%": abs(ind["rot_anual"] - 0.516) < 1e-6,
            }
            for texto, ok in revisiones.items():
                st.write(("✅ " if ok else "❌ ") + texto)
