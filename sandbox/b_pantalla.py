import json
import sys
import time
from pathlib import Path

import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from ui import comparativo
from ui.controles import render
from ui.tema import AMBAR, GRIS, aplicar_estilos

CARPETA_FIXTURES = RAIZ / "contrato" / "fixtures"
RUTA_EMPRESAS = RAIZ / "data" / "processed"/"empresas.parquet"
MOSTRAR_TIEMPO = True
LIMITE_MS = 300


def _cargar(prefijo):
    """Busca contrato/fixtures/<prefijo>_*.json, por ejemplo 01_aguinaldo.json."""
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


@st.fragment
def panel(perfil):
    """Controles + panel central. Al mover una palanca solo se vuelve a correr esta función."""
    col_izq, col_centro = st.columns([1.4, 2.6], gap="large")

    with col_izq:
        st.markdown('<div class="titulo-col">Palancas</div>', unsafe_allow_html=True)
        palancas_movidas, cambio = render(perfil)

    datos = motor_falso(palancas_movidas)

    with col_centro:
        st.markdown('<div class="titulo-col">Comparativo</div>', unsafe_allow_html=True)
        comparativo.render(datos)
        comparativo.cifras_pesos(datos)
        # Dispersión: X = última palanca movida (si no hay, salario inicial), Y = rotación anual
        if RUTA_EMPRESAS.exists():
            palanca_x = cambio["palanca"] if cambio else "sal_dia_ini"
            valor_x = palancas_movidas.get(palanca_x, perfil["palancas"][palanca_x])
            comparativo.dispersion(datos, comparativo.cargar_empresas(RUTA_EMPRESAS), palanca_x, valor_x)
        else:
            st.warning(f"No encuentro {RUTA_EMPRESAS}")
        st.caption(f"Fixture en pantalla: {datos['_archivo']}")

    if MOSTRAR_TIEMPO:
        t_click = st.session_state.pop("_t_click", None)
        if t_click is not None:  # solo cuando hubo un clic; si no, se conserva la última medición
            st.session_state["_ultimo_ms"] = (time.perf_counter() - t_click) * 1000
        ms = st.session_state.get("_ultimo_ms")
        if ms is not None:
            color = AMBAR if ms > LIMITE_MS else GRIS
            st.markdown(
                f'<div style="position:fixed;bottom:8px;right:12px;z-index:999;font-size:13px;color:{color}">'
                f"clic → dibujo: {ms:.0f} ms</div>",
                unsafe_allow_html=True,
            )


base = _cargar("05") 
panel(base["empresa"])