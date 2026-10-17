"""Radar de Decisiones: selector + palancas, comparativo y explicación, conectados al motor real."""

import copy
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

from motor.api import calcular_estado
from ui import comparativo, controles, explicacion, selector, supuestos
from ui.tema import AMBAR, GRIS, aplicar_estilos

RAIZ = Path(__file__).parent
RUTA_EMPRESAS = RAIZ / "data" / "processed" / "empresas.parquet"
MOSTRAR_TIEMPO = True
LIMITE_MS = 300
USAR_FRAGMENTO = True

st.set_page_config(layout="wide")
aplicar_estilos()


def _alternar_palanca():
    st.session_state["_ver_palanca"] = not st.session_state.get("_ver_palanca", False)


def _titulo(texto):
    st.markdown(f'<div class="titulo-col">{texto}</div>', unsafe_allow_html=True)


def _guardar_escenario(estado, explicado):
    """Captura lo que hay en pantalla: el estado completo y, si está vigente, su explicación."""
    vigente = explicado is not None and not explicacion.falta_explicar(estado, explicado)
    guardados = st.session_state.setdefault("escenarios_guardados", [])
    guardados.append({
        "hora": datetime.now().isoformat(timespec="seconds"),
        "estado": copy.deepcopy(estado),
        "explicacion": (explicado.get("explicacion") or {}).get("texto") if vigente else None,
    })
    st.toast(f"Escenario guardado ({len(guardados)})")


def _pantalla(empresas):
    """Todo vive en un fragmento: al mover una palanca no se recarga la página completa."""
    st.markdown('<div class="titulo-app">Radar de Decisiones</div>', unsafe_allow_html=True)
    subtitulo = st.empty()
    col_izq, col_centro, col_der = st.columns([1.15, 2.2, 1.65], gap="large")

    # Izquierda: selector arriba; controles con Restablecer y Guardar abajo
    with col_izq:
        _titulo("Palancas")
        perfil = selector.render(empresas)
        if perfil is None:
            return
        palancas_movidas, cambio, guardar = controles.render(perfil, con_guardar=True)
        nota_guardados = st.empty()

    n = perfil.get("plantilla_op")
    subtitulo.markdown(
        f'<div class="subtitulo">{perfil["id"]}' + (f" - Plantilla {n:,}" if n is not None else "") + "</div>",
        unsafe_allow_html=True,
    )

    # Centro: se arman los espacios en orden y se llenan cuando hay estado.

    with col_centro:
        _titulo("Comparativo")
        zona_tabla = st.container()
        zona_pesos = st.container()
        zona_extra = st.container()
    with zona_pesos:
        c_medida, c_brecha, c_ajustes = st.columns([1, 1, 0.4], vertical_alignment="center")
        with c_ajustes:
            ajustes = supuestos.render()

    empresas_motor = comparativo.con_mi_empresa(empresas, perfil)
    try:
        estado = calcular_estado(empresas_motor, perfil, palancas_movidas, cambio, ajustes)
    except ValueError as error:
        st.error(str(error))
        return

    explicado = st.session_state.get("estado_explicado")
    if guardar:
        _guardar_escenario(estado, explicado)
    total = len(st.session_state.get("escenarios_guardados", []))
    if total:
        nota_guardados.markdown(f'<div class="texto-gris">{total} escenario(s) guardado(s)</div>', unsafe_allow_html=True)

    with zona_tabla:
        comparativo.render(estado)
    with zona_pesos:
        comparativo.cifras_pesos(estado, (c_medida, c_brecha))
    with zona_extra:
        ver = st.session_state.get("_ver_palanca", False)
        st.button(
            "Ocultar gráfica por palanca" if ver else "Ver gráfica por palanca",
            on_click=_alternar_palanca, key="btn_palanca",
        )
        if ver:
            palanca_x = cambio["palanca"] if cambio else "sal_dia_ini"
            valor_x = palancas_movidas.get(palanca_x, perfil["palancas"].get(palanca_x))
            comparativo.dispersion(estado, empresas, palanca_x, valor_x)

    # Derecha: Explicar, explicación y, debajo, la rotación por grupo
    with col_der:
        _titulo("Explicación")
        pulsado = st.button(
            "Explicar", type="primary", key="btn_explicar", use_container_width=True,
            disabled=not palancas_movidas, help="Mueve al menos una palanca y explica el escenario cuando esté listo.",
        )
        contenedor = st.container()
        with st.container():
            comparativo.distribucion_rotacion(estado, empresas)
        if pulsado:
            explicacion.render(contenedor, estado, explicado)
            st.session_state["estado_explicado"] = estado
        elif explicado is not None:
            if explicacion.falta_explicar(estado, explicado):
                explicacion.aviso_pendiente(contenedor)
            else:
                explicacion.mostrar(contenedor, explicado)

    if MOSTRAR_TIEMPO:
        t_click = st.session_state.pop("_t_click", None)
        if t_click is not None:
            st.session_state["_ultimo_ms"] = (time.perf_counter() - t_click) * 1000
        ms = st.session_state.get("_ultimo_ms")
        if ms is not None:
            color = AMBAR if ms > LIMITE_MS else GRIS
            st.markdown(
                f'<div style="position:fixed;bottom:8px;right:12px;z-index:999;font-size:13px;color:{color}">'
                f"clic → dibujo: {ms:.0f} ms</div>",
                unsafe_allow_html=True,
            )


pantalla = st.fragment(_pantalla) if USAR_FRAGMENTO else _pantalla
pantalla(comparativo.cargar_empresas(RUTA_EMPRESAS))