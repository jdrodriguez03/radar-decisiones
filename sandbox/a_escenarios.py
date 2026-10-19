"""Sandbox de Aleja: guardar y comparar escenarios A y B.

Correr desde la raíz del repositorio: streamlit run sandbox/a_escenarios.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from config import RUTA_SUPUESTOS
from motor.api import calcular_estado
from motor.datos import cargar
from ui import escenarios
from ui.controles import render as render_controles
from ui.selector import perfil_demo


# se crea un subdirectorio "sandbox" para que no se confunda con el módulo "escenarios" de ui
# función para cargar empresas desde el módulo de datos, con cache para no recargar en cada interacción
@st.cache_data
def _empresas():
    return cargar()


def _dinero(valor):
    return "—" if valor is None else f"${valor:,.0f}"


def _porcentaje(valor):
    return "—" if valor is None else f"{valor:.1%}"


st.set_page_config(page_title="Sandbox A · escenarios", layout="wide")
st.title("Sandbox A · escenarios A y B")
st.caption("Ajusta COMPAÑIA 36, guarda dos estados y compara sus resultados.")

empresas = _empresas()
perfil = perfil_demo(empresas, "COMPAÑIA 36")
supuestos = json.loads(RUTA_SUPUESTOS.read_text(encoding="utf-8"))
palancas_movidas, cambio = render_controles(perfil)
estado_actual = calcular_estado(
    empresas,
    perfil,
    palancas_movidas,
    cambio,
    supuestos,
)
# se guardan los escenarios en session_state para que persistan entre interacciones
guardados = st.session_state.get(escenarios.CLAVE_ESCENARIOS, [])
col_guardar, col_limpiar = st.columns([1, 1])
with col_guardar: #se guarda el escenario actual en la lista de escenarios guardados
    if st.button("Guardar escenario", disabled=len(guardados) >= 2):
        guardado = escenarios.guardar(estado_actual)
        st.success(f"Escenario {guardado['nombre']} guardado.")
        guardados = st.session_state[escenarios.CLAVE_ESCENARIOS]
with col_limpiar: #se limpia la lista de escenarios guardados
    if st.button("Limpiar escenarios", disabled=not guardados):
        st.session_state.pop(escenarios.CLAVE_ESCENARIOS, None)
        st.rerun()
# se muestran los escenarios guardados y sus diferencias
if len(guardados) == 1:
    st.info("Escenario A guardado. Cambia las palancas y guarda el escenario B.")
elif len(guardados) < 2:
    st.info("Guarda el primer escenario para iniciar la comparación.")
else:
    escenario_a, escenario_b = guardados
    estado_a = escenario_a["estado"]
    estado_b = escenario_b["estado"]
    diferencias = escenarios.comparar_escenarios(estado_a, estado_b)
# se muestran los escenarios A y B en columnas
    col_a, col_b = st.columns(2, gap="large")
    for columna, escenario, metricas in (
        (col_a, escenario_a, estado_a),
        (col_b, escenario_b, estado_b),
    ):
        nombre = escenario["nombre"]
        with columna:
            st.subheader(f"Escenario {nombre}")
            st.caption(f"Empresa: {escenario['empresa']['id']}")
            st.write("Palancas movidas:", escenario["palancas_movidas"] or "Ninguna")
            st.write("Supuestos:", escenario["supuestos"])
            st.metric("Empresas en el grupo", metricas["grupo"]["n"])
            st.metric(
                "Rotación anual del grupo",
                _porcentaje(metricas["grupo"]["indicadores"]["rot_anual"]),
            )
            st.metric("Señal", metricas["senal"]["etiqueta"])
            st.metric(
                "Costo anual de la medida",
                _dinero(metricas["pesos"]["costo_medida_anual"]),
            )
            st.metric(
                "Costo anual de la brecha",
                _dinero(metricas["pesos"]["costo_brecha_anual"]),
            )

    st.subheader("Diferencias")
    mayor_grupo = diferencias["n_grupo"]["mayor"]
    menor_medida = diferencias["costo_medida"]["menor"]
    menor_brecha = diferencias["costo_brecha"]["menor"]
    st.write(
        f"**Grupo más grande:** "
        f"{'ninguno; tienen el mismo tamaño' if mayor_grupo == 'empate' else f'escenario {mayor_grupo}'}."
    )
    st.write(
        f"**Menor costo de medida:** "
        f"{'igual en ambos' if menor_medida == 'empate' else f'escenario {menor_medida}'}."
    )
    st.write(
        f"**Menor costo de brecha:** "
        f"{'igual en ambos' if menor_brecha == 'empate' else f'escenario {menor_brecha}'}."
    )
# se muestran las diferencias B − A
    delta_n = diferencias["n_grupo"]["diferencia_b_menos_a"]
    delta_rotacion = diferencias["rotacion_grupo"]["diferencia_b_menos_a"]
    delta_medida = diferencias["costo_medida"]["diferencia_b_menos_a"]
    delta_brecha = diferencias["costo_brecha"]["diferencia_b_menos_a"]
    st.caption(
        "Diferencias B − A: "
        f"grupo {delta_n:+g}; "
        f"rotación {_porcentaje(delta_rotacion)}; "
        f"medida {_dinero(delta_medida)}; "
        f"brecha {_dinero(delta_brecha)}."
    )
    senal_a = diferencias["senal"]["a"]
    senal_b = diferencias["senal"]["b"]
    if diferencias["senal"]["cambio"]:
        st.info(
            f"La señal cambia de {senal_a['etiqueta']} (A) a {senal_b['etiqueta']} (B)."
        )
    else:
        st.caption(f"La señal es igual en ambos: {senal_a['etiqueta']}.")
