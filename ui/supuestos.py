"""Panel ⚙ con costo por baja y costo por ruta. Dueño: Juanes."""

"""Panel ⚙ con costo por baja y costo por ruta. Dueño: Juanes."""
import json

import streamlit as st

from config import RUTA_SUPUESTOS

_K = "d_supuestos_"  # prefijo de las llaves en st.session_state


def por_defecto():
    """Lee los valores por defecto de data/processed/supuestos.json."""
    return json.loads(RUTA_SUPUESTOS.read_text(encoding="utf-8"))


def render():
    """Devuelve el dict de supuestos."""
    base = por_defecto()
    with st.popover("⚙"):
        st.caption("Supuestos editables. Los valores por defecto se validan con RH.")
        costo_baja = st.number_input(
            ":orange[Costo por baja ($)]",
            min_value=0,
            value=int(base["costo_por_baja"]),
            step=1000,
            key=_K + "baja",
        )
        costo_ruta = st.number_input(
            ":orange[Costo mensual por ruta ($)]",
            min_value=0,
            value=int(base["costo_ruta_mensual"]),
            step=1000,
            key=_K + "ruta",
        )
    return {"costo_por_baja": float(costo_baja), "costo_ruta_mensual": float(costo_ruta)}

