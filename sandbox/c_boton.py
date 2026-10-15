"""Sandbox de Julian: el botón Explicar con el motor real.

Correr desde la raíz del repo:  streamlit run sandbox/c_boton.py

Izquierda: empresa y palancas (como los controles de Gaby, pero simples).
Derecha: el panel de explicación exactamente como lo conectará app.py:
  - pulsar Explicar  -> ui.explicacion.render (IA, caché o plantilla)
  - cifras cambiadas -> ui.explicacion.aviso_pendiente (el texto viejo se oculta)
  - nada cambió      -> ui.explicacion.mostrar (redibuja sin llamar a la IA)
Abajo, "Detrás de escena": lo que se le manda a la IA y si el texto cumple las reglas.

Sin llave en .streamlit/secrets.toml la explicación sale de la plantilla: sirve igual para ver el flujo.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para poder importar config, motor, ia y ui

import streamlit as st

import config
from ia.prompts import anterior_util, armar_mensaje
from ia.reglas import revisar
from ia.validador import cifras_inventadas
from motor.api import calcular_estado
from motor.datos import cargar
from ui import explicacion
from ui.selector import perfil_demo

EMPRESAS_DEMO = ["COMPAÑIA 36", "COMPAÑIA 29", "COMPAÑIA 15"]
ETIQUETAS = {
    "sal_dia_ini": "Salario diario inicial ($)",
    "aguinaldo_op": "Aguinaldo (días)",
    "prima_vac_op": "Prima vacacional",
    "vales_op": "Vales de despensa",
    "rutas_x100": "Rutas por cada 100",
}
FUENTES = {"cache": "Caché", "llm": "IA en vivo (validada)", "plantilla": "Plantilla de respaldo"}


@st.cache_data
def empresas():
    return cargar()


def hay_llave():
    try:
        return bool(os.environ.get("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY"))
    except Exception:  # noqa: BLE001  sin secrets.toml
        return False


st.set_page_config(page_title="Sandbox · botón Explicar", layout="wide")
st.title("Sandbox · botón Explicar")
st.caption("Mueve una o varias palancas y pulsa Explicar. La IA solo escribe al pulsar.")

df = empresas()
supuestos = json.loads(config.RUTA_SUPUESTOS.read_text(encoding="utf-8"))
col_izq, col_der = st.columns([1, 1.4], gap="large")

with col_izq:
    empresa_id = st.selectbox("Empresa", EMPRESAS_DEMO)
    perfil = perfil_demo(df, empresa_id)
    if st.session_state.get("empresa") != empresa_id:  # otra empresa: todo vuelve a cero (como Restablecer)
        st.session_state.update(empresa=empresa_id, explicado=None)
        for p in config.PALANCAS:
            st.session_state.pop(f"palanca_{p}", None)

    movidas = {}
    for palanca, (minimo, maximo, paso) in config.PALANCAS.items():
        real = perfil["palancas"].get(palanca)
        if real is None:
            continue
        valor = st.number_input(
            f"{ETIQUETAS[palanca]} · real {real:g}", min_value=float(minimo), max_value=float(maximo),
            value=float(min(max(real, minimo), maximo)), step=float(paso), key=f"palanca_{palanca}",
        )
        if abs(valor - real) > 1e-9:
            movidas[palanca] = valor
    supuestos["costo_por_baja"] = st.number_input("⚙ Costo por baja", value=float(supuestos["costo_por_baja"]), step=5000.0)

    ultima = list(movidas)[-1] if movidas else None
    cambio = {"palanca": ultima, "de": perfil["palancas"][ultima], "a": movidas[ultima]} if ultima else None
    estado = calcular_estado(df, perfil, movidas, cambio, supuestos)

    g, r = estado["grupo"], estado["resto"]
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Empresas que ya lo hacen", g["n"])
    c2.metric("Pierden al año", f"{g['indicadores']['rot_anual']:.0%}")
    c3.metric("Las demás", f"{r['indicadores']['rot_anual']:.0%}" if r["n"] else "—")
    st.caption("Las cifras cambian al instante; la explicación no.")

with col_der:
    st.subheader("Explicación")
    if not hay_llave():
        st.caption("Sin llave de la API: la explicación sale de la plantilla.")
    explicado = st.session_state.get("explicado")  # el "anterior" es la última combinación explicada
    panel = st.container(border=True)
    if st.button("Explicar", type="primary"):
        explicacion.render(panel, estado, explicado)
        st.session_state["explicado"] = estado
        st.session_state["fuente"] = estado["explicacion"]["fuente"]
        explicado = estado
    elif explicacion.falta_explicar(estado, explicado):
        explicacion.aviso_pendiente(panel)
    else:
        explicacion.mostrar(panel, explicado)

    st.subheader("Detrás de escena")
    with st.expander("Lo que se le manda a la IA si pulsas Explicar ahora", expanded=True):
        mensaje = armar_mensaje(estado, explicado)
        st.code(mensaje.split("Resultado actual")[0].strip(), language=None)
        if anterior_util(estado, explicado) is None:
            st.caption("Sin paso anterior útil: es la primera comparación de esta empresa.")
    if explicado and explicado.get("explicacion"):
        texto = explicado["explicacion"]["texto"]
        fallas = revisar(texto, explicado)
        inventadas = cifras_inventadas(texto, explicado)
        st.markdown(f"**Fuente del último texto:** {FUENTES[st.session_state.get('fuente', 'plantilla')]}")
        st.markdown(f"**Cifras:** {'todas están en los datos' if not inventadas else 'inventa ' + str(inventadas)}")
        st.markdown(f"**Reglas:** {'cumple todas' if not fallas else '; '.join(fallas)} · {len(texto.split())} palabras")
