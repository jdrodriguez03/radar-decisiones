"""Radar de Decisiones: selector + palancas, comparativo y explicación, conectados al motor real."""

import time
from pathlib import Path

import streamlit as st

from motor.api import calcular_estado
from ui import comparativo, controles, explicacion, selector, supuestos
from ui.tema import AMBAR, GRIS, aplicar_estilos

RAIZ = Path(__file__).parent
RUTA_EMPRESAS = RAIZ / "data" / "processed" / "empresas.parquet"
MOSTRAR_TIEMPO = True
LIMITE_MS = 300

st.set_page_config(layout="wide")
aplicar_estilos()


def _firma(palancas):
    """Identifica una combinación de palancas movidas."""
    return tuple(sorted((k, round(v, 6)) for k, v in palancas.items()))


def _alternar_palanca():
    st.session_state["_ver_palanca"] = not st.session_state.get("_ver_palanca", False)


def _titulo(texto):
    st.markdown(f'<div class="titulo-col">{texto}</div>', unsafe_allow_html=True)


@st.fragment
def pantalla(empresas):
    """Todo vive en un fragmento: al mover una palanca no se recarga la página completa."""
    st.markdown('<div class="titulo-app">Radar de Decisiones</div>', unsafe_allow_html=True)
    subtitulo = st.empty()
    col_izq, col_centro, col_der = st.columns([1.3, 2.2, 1.5], gap="large")

    # Columna izquierda: selector arriba, controles abajo
    with col_izq:
        _titulo("Palancas")
        perfil = selector.render(empresas)
        if perfil is None:  # "Mi empresa" aún no se envía; el selector ya avisa qué falta
            return
        palancas_movidas, cambio = controles.render(perfil)

    n = perfil.get("plantilla_op")
    subtitulo.markdown(
        f'<div class="subtitulo">{perfil["id"]}' + (f" - Plantilla {n:,}" if n is not None else "") + "</div>",
        unsafe_allow_html=True,
    )

    # Columna central: se arman los espacios en orden y se llenan cuando hay estado.
    with col_centro:
        _titulo("Comparativo")
        zona_graficas = st.container()
        zona_pesos = st.container()
        zona_extra = st.container()
    with zona_pesos:
        c_medida, c_brecha, c_ajustes = st.columns([1, 1, 0.25], vertical_alignment="center")
        with c_ajustes:
            ajustes = supuestos.render()

    try:
        estado = calcular_estado(empresas, perfil, palancas_movidas, cambio, ajustes)
    except ValueError as error:
        st.error(str(error))
        return

    niveles = {p: palancas_movidas.get(p, v) for p, v in perfil["palancas"].items()}
    with zona_graficas:
        comparativo.render(estado)
        g_b, g_c = st.columns(2)
        with g_b:
            st.markdown('<div class="grafica-titulo">Rotación anual: grupo y resto</div>', unsafe_allow_html=True)
            comparativo.distribucion_rotacion(estado, empresas)
        with g_c:
            st.markdown('<div class="grafica-titulo">Qué hace distinto el grupo</div>', unsafe_allow_html=True)
            comparativo.palancas_grupo(estado, empresas, niveles)
        comparativo.en_comun(estado)
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

    # Columna derecha: Explicar solo se llama al pulsarlo
    with col_der:
        _titulo("Explicación")
        explicado = st.session_state.get("estado_explicado")
        misma_empresa = explicado is not None and explicado["empresa"]["id"] == estado["empresa"]["id"]
        anterior = explicado if misma_empresa else None  # la última combinación explicada, no el último movimiento
        pulsado = st.button(
            "Explicar", type="primary", key="btn_explicar", use_container_width=True,
            disabled=not palancas_movidas, help="Mueve al menos una palanca y explica el escenario cuando esté listo.",
        )
        contenedor = st.container()
        if pulsado:
            explicacion.render(contenedor, estado, anterior)
            st.session_state["estado_explicado"] = estado
        elif misma_empresa and _firma(explicado["palancas_movidas"]) != _firma(palancas_movidas):
            explicacion.aviso_pendiente(contenedor)

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


pantalla(comparativo.cargar_empresas(RUTA_EMPRESAS))