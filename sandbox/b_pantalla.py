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
RUTA_EMPRESAS = RAIZ / "data" / "processed" / "empresas.parquet"
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


def _firma(palancas_movidas):
    """Identifica el escenario: las palancas movidas y sus valores."""
    return tuple(sorted((k, round(v, 6)) for k, v in palancas_movidas.items()))


def motor_ia_falso(datos, palancas_movidas):
    """Reemplaza al backend de IA: devuelve el texto del fixture del escenario.

    Aquí se llamará al modelo real. Solo se invoca desde el botón, una vez por escenario.
    """
    return (datos.get("explicacion") or {}).get("texto")


def _alternar_palanca():
    st.session_state["_ver_palanca"] = not st.session_state.get("_ver_palanca", False)


@st.fragment
def panel(perfil):
    """Controles + panel central. Al mover una palanca solo se vuelve a correr esta función."""
    col_izq, col_centro, col_der = st.columns([1.3, 2.2, 1.5], gap="large")

    with col_izq:
        st.markdown('<div class="titulo-col">Palancas</div>', unsafe_allow_html=True)
        palancas_movidas, cambio = render(perfil)

    datos = motor_falso(palancas_movidas)
    firma = _firma(palancas_movidas)

    with col_centro:
        st.markdown('<div class="titulo-col">Comparativo</div>', unsafe_allow_html=True)
        comparativo.render(datos)

        if RUTA_EMPRESAS.exists():
            empresas = comparativo.cargar_empresas(RUTA_EMPRESAS)
            niveles = {p: palancas_movidas.get(p, v) for p, v in perfil["palancas"].items()}
            g_b, g_c = st.columns(2)
            with g_b:
                st.markdown('<div class="grafica-titulo">Rotación anual: grupo y resto</div>', unsafe_allow_html=True)
                comparativo.distribucion_rotacion(datos, empresas)
            with g_c:
                st.markdown('<div class="grafica-titulo">Qué hace distinto el grupo</div>', unsafe_allow_html=True)
                comparativo.palancas_grupo(datos, empresas, niveles)
            comparativo.en_comun(datos)
        else:
            st.warning(f"No encuentro {RUTA_EMPRESAS}")

        comparativo.cifras_pesos(datos)

        ver = st.session_state.get("_ver_palanca", False)
        st.button(
            "Ocultar gráfica por palanca" if ver else "Ver gráfica por palanca",
            on_click=_alternar_palanca, key="btn_palanca",
        )
        if ver:
            if RUTA_EMPRESAS.exists():
                palanca_x = cambio["palanca"] if cambio else "sal_dia_ini"
                valor_x = palancas_movidas.get(palanca_x, perfil["palancas"][palanca_x])
                comparativo.dispersion(
                    datos, comparativo.cargar_empresas(RUTA_EMPRESAS), palanca_x, valor_x
                )
            else:
                st.warning(f"No encuentro {RUTA_EMPRESAS}")
        st.caption(f"Fixture en pantalla: {datos['_archivo']}")

    with col_der:
        st.markdown('<div class="titulo-col">Explicación</div>', unsafe_allow_html=True)
        generadas = st.session_state.setdefault("_explicaciones", {})

        if st.button("Generar explicación", key="btn_ia", disabled=not palancas_movidas,
                     help="Mueve al menos una palanca y, cuando el escenario esté listo, genera la explicación."):
            if firma not in generadas:
                texto = motor_ia_falso(datos, palancas_movidas)
                if texto is not None:
                    generadas[firma] = texto
            st.session_state["_firma_ia"] = firma
        firma_ia = st.session_state.get("_firma_ia")
        if firma_ia is not None:
            if firma_ia == firma and firma not in generadas:
                st.info(
                    f"Este escenario ({datos['_archivo']}) aún no tiene texto de ejemplo. "
                    "Con el backend de IA conectado, la explicación se generará aquí."
                )
            elif firma_ia == firma:
                st.markdown(f'<div class="explicacion">{generadas[firma_ia]}</div>', unsafe_allow_html=True)
            else:
                st.warning("El escenario cambió. Vuelve a generar la explicación para que coincida con las gráficas.")

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


base = _cargar("05")
panel(base["empresa"])