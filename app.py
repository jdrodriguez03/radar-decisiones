"""Radar de Decisiones: selector + palancas, comparativo y explicación, conectados al motor real."""

import copy
import time
from datetime import datetime

import streamlit as st

from config import RUTA_EMPRESAS
from motor.api import calcular_estado
from ui import (
    comparativo,
    controles,
    escenarios,
    explicacion,
    historial,
    selector,
    supuestos,
)
from ui.tema import AMBAR, GRIS, aplicar_estilos

MOSTRAR_TIEMPO = True
LIMITE_MS = 300
USAR_FRAGMENTO = True

EXTRAS = {
    "escenarios": True,
    "historial": True,
    "tamano_parecido": True,
    "semaforo": True,
}

st.set_page_config(layout="wide")
aplicar_estilos()


def _titulo(texto):
    st.markdown(f'<div class="titulo-col">{texto}</div>', unsafe_allow_html=True)


def _avisar_mi_empresa(perfil):
    """Al pulsar «Usar mi empresa» los cambios quedan arriba, fuera de la vista; un aviso confirma que se aplicaron."""
    firma = (perfil["id"], perfil.get("plantilla_op"), str(sorted(perfil["palancas"].items())))
    anterior = st.session_state.get("_firma_mostrada")
    st.session_state["_firma_mostrada"] = firma
    if anterior is not None and anterior != firma and perfil["id"] == selector.MI_EMPRESA_ID:
        st.toast("Datos de su empresa cargados: las palancas y el comparativo ya los usan.", icon="✅")


def _olvidar_explicacion():
    """Cambiar el universo (tamaño parecido) cambia el grupo: la última explicación ya no corresponde."""
    st.session_state.pop("estado_explicado", None)


def _limpiar_ab():
    st.session_state.pop(escenarios.CLAVE_ESCENARIOS, None)


def _calcular(empresas, perfil, palancas_movidas, cambio, ajustes, solo_tamano, aviso):
    """Llama al motor. Si «Mi empresa» no cae en ninguna banda de tamaño, compara con todas y lo dice."""
    if solo_tamano:
        try:
            return calcular_estado(empresas, perfil, palancas_movidas, cambio, ajustes, solo_tamano=True)
        except ValueError:
            aviso.markdown(
                '<div class="palanca-aviso">Su plantilla no cae en ninguna banda de tamaño de la encuesta: '
                "se compara con todas las empresas.</div>",
                unsafe_allow_html=True,
            )
    return calcular_estado(empresas, perfil, palancas_movidas, cambio, ajustes)


def _guardar_escenario(estado, explicado):
    """Captura lo que hay en pantalla: el estado completo y, si está vigente, su explicación."""
    vigente = explicado is not None and not explicacion.falta_explicar(estado, explicado)
    guardados = st.session_state.setdefault("escenarios_guardados", [])
    guardados.append({
        "hora": datetime.now().astimezone().isoformat(timespec="seconds"),
        "estado": copy.deepcopy(estado),
        "explicacion": (explicado.get("explicacion") or {}).get("texto") if vigente else None,
    })
    if not EXTRAS["escenarios"]:
        st.toast(f"Escenario guardado ({len(guardados)})")
        return
    try:
        nombre = escenarios.guardar(estado)["nombre"]
        st.toast(f"Escenario {nombre} guardado")
    except ValueError:
        st.toast("Ya hay un escenario A y uno B. Pulse «Limpiar A y B» para comparar otros.", icon="⚠️")


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
        _avisar_mi_empresa(perfil)
        solo_tamano = False
        if EXTRAS["tamano_parecido"]:
            solo_tamano = st.toggle(
                "Solo tamaño parecido", value=st.session_state.get("_solo_tamano", False),
                key="solo_tamano", on_change=_olvidar_explicacion,
                help="Compara solo con empresas de la misma banda de plantilla que la suya: chica, mediana o grande.",
            )
            st.session_state["_solo_tamano"] = solo_tamano
        aviso_tamano = st.empty()
        palancas_movidas, cambio, guardar = controles.render(perfil, con_guardar=True)
        nota_guardados = st.empty()
        zona_resumen = st.container()  # «Descargar resumen»: se llena al final, cuando ya hay explicación

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
        zona_supuestos = st.container()
        zona_extra = st.container()
    with zona_pesos:
        c_medida, c_brecha = st.columns(2, vertical_alignment="center")
    with zona_supuestos:
        # Título y ⚙ juntos y centrados, en línea con el texto ámbar del supuesto que queda justo encima
        fila = st.container(horizontal=True, horizontal_alignment="center", vertical_alignment="center", gap="small")
        with fila:
            st.markdown('<div class="supuestos-titulo">Modificación de supuestos</div>', unsafe_allow_html=True,
                        width="content")
            ajustes = supuestos.render()

    try:
        estado = _calcular(empresas, perfil, palancas_movidas, cambio, ajustes, solo_tamano, aviso_tamano)
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
        if EXTRAS["escenarios"]:
            comparativo.escenarios_ab(st.session_state.get(escenarios.CLAVE_ESCENARIOS, []), _limpiar_ab)

    # Derecha, en este orden: título, Explicar, explicación de la IA (o el aviso de que hay cambios sin explicar),
    # la gráfica de rotación, el semáforo y el historial.
    with col_der:
        _titulo("Explicación")
        pulsado = st.button(
            "Explicar", type="primary", key="btn_explicar", width="stretch",
            disabled=not palancas_movidas, help="Mueve al menos una palanca y explica el escenario cuando esté listo.",
        )
        contenedor = st.container()
        with st.container():
            comparativo.distribucion_rotacion(estado, empresas)
        if EXTRAS["semaforo"]:
            explicacion.semaforo(st.container(), estado)
        if pulsado:
            explicacion.render(contenedor, estado, explicado)
            st.session_state["estado_explicado"] = estado
            if EXTRAS["historial"]:
                st.session_state["historial"] = historial.agregar(st.session_state.get("historial", []), estado)
        elif explicado is not None:
            if explicacion.falta_explicar(estado, explicado):
                explicacion.aviso_pendiente(contenedor)
            else:
                explicacion.mostrar(contenedor, explicado)
        if EXTRAS["historial"]:
            historial.render(st.session_state.get("historial", []))

   
    explicacion.boton_resumen(
        zona_resumen, estado, st.session_state.get("escenarios_guardados", []), st.session_state.get("estado_explicado"),
    )

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
