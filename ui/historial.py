
"""Historial de explicaciones. Dueño: Juanes (persona D).

Para qué sirve: cada vez que el directivo mueve una palanca, la IA escribe una
explicación nueva y la anterior desaparece del panel derecho. El historial guarda
esas explicaciones viejas para que, en la demo, se pueda ver el recorrido completo
("primero subí el aguinaldo, luego la prima, luego el salario") sin perder nada.

Cómo se usa desde app.py (lo conecta Gaby en el bloque 6, si se aprueba el extra):

    from ui import historial

    if "historial" not in st.session_state:
        st.session_state.historial = []
    # ... después de calcular el estado y de tener su explicación:
    st.session_state.historial = historial.agregar(st.session_state.historial, estado)
    historial.render(st.session_state.historial)

Al presionar Restablecer o cambiar de empresa, app.py debe poner
st.session_state.historial = [] para empezar de cero.

Este archivo solo DIBUJA y da formato: no calcula cifras de negocio (regla de ui/).
"""
from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# 1. Cómo se escribe cada palanca en el historial
# ---------------------------------------------------------------------------
# Cada palanca recibe su valor anterior (de) y el nuevo (a) y devuelve el texto
# corto que ve el directivo. Los valores llegan como en el contrato: la prima 0.25
# significa 25%, los vales 0.09 significan 9%. La unidad ("días") se dice una sola
# vez al final porque "aguinaldo 15 → 20 días" se lee más rápido en el proyector.
FORMATO_PALANCAS = {
    "sal_dia_ini": lambda de, a: f"salario inicial ${de:,.0f} → ${a:,.0f}",
    "aguinaldo_op": lambda de, a: f"aguinaldo {de:g} → {a:g} días",
    "prima_vac_op": lambda de, a: f"prima vacacional {de:.0%} → {a:.0%}",
    "vales_op": lambda de, a: f"vales {de * 100:g}% → {a * 100:g}%",
    "rutas_x100": lambda de, a: f"rutas {de:g} → {a:g} por cada 100",
}

MAXIMO_ENTRADAS = 10  # más de 10 ya no se lee en el proyector; las más viejas se descartan


def describir_cambio(cambio: dict | None) -> str:
    """Convierte el campo "cambio" del contrato en un texto corto.

    {"palanca": "aguinaldo_op", "de": 15, "a": 20}      -> "aguinaldo 15 → 20 días"
    {"palanca": "prima_vac_op", "de": 0.25, "a": 0.5}   -> "prima vacacional 25% → 50%"
    {"palanca": "sal_dia_ini", "de": 323.61, "a": 350}  -> "salario inicial $324 → $350"
    None (estado inicial, nadie ha movido nada)        -> "situación inicial"
    """
    if not cambio:
        return "situación inicial"
    palanca, de, a = cambio["palanca"], cambio["de"], cambio["a"]
    if palanca not in FORMATO_PALANCAS:  # palanca desconocida: no truena, la muestra tal cual
        return f"{palanca} {de:g} → {a:g}"
    return FORMATO_PALANCAS[palanca](de, a)


# ---------------------------------------------------------------------------
# 2. Construir el historial (funciones puras: no dibujan, se pueden probar)
# ---------------------------------------------------------------------------
def nueva_entrada(estado: dict) -> dict | None:
    """Toma un estado del contrato y saca solo lo que el historial necesita mostrar.

    Devuelve None si no hay nada que guardar: estado inicial (sin cambio) o
    estado que todavía no tiene explicación (la IA no ha terminado de escribir).
    """
    explicacion = estado.get("explicacion")
    if estado.get("cambio") is None or not explicacion or not explicacion.get("texto"):
        return None
    return {
        "empresa": estado["empresa"]["id"],
        "cambio": describir_cambio(estado["cambio"]),
        "palancas_movidas": dict(estado["palancas_movidas"]),
        "texto": explicacion["texto"],
        "fuente": explicacion.get("fuente", "plantilla"),
        "n": estado["grupo"]["n"],
        "senal": estado["senal"]["etiqueta"],
        "completado": estado["grupo"]["completado"],
    }


def agregar(historial: list[dict], estado: dict, maximo: int = MAXIMO_ENTRADAS) -> list[dict]:
    """Devuelve una lista NUEVA con la entrada del estado agregada al final.

    - No modifica la lista original (así Streamlit no se confunde entre recargas).
    - Si el estado no tiene nada que guardar, devuelve el historial igual.
    - Si el último renglón ya es este mismo estado (Streamlit recarga la página y
      llama a agregar dos veces con el mismo estado), no lo repite.
    - Si se cambia de empresa, empieza un historial nuevo.
    - Guarda como máximo `maximo` entradas: se descartan las más viejas.
    """
    entrada = nueva_entrada(estado)
    if entrada is None:
        return list(historial)
    if historial and historial[-1]["empresa"] != entrada["empresa"]:
        historial = []
    if historial and historial[-1]["palancas_movidas"] == entrada["palancas_movidas"]:
        return list(historial)
    return (list(historial) + [entrada])[-maximo:]


# ---------------------------------------------------------------------------
# 3. Dibujar
# ---------------------------------------------------------------------------
ICONO_FUENTE = {"llm": "IA", "cache": "IA (guardada)", "plantilla": "texto de respaldo"}


def _sin_latex(texto: str) -> str:
    """Streamlit lee $...$ como fórmula matemática; se escapa cada $ para que se vea como pesos."""
    return texto.replace("$", r"\$")


def render(historial: list[dict]) -> None:
    """Dibuja el historial dentro de un expander, con la entrada más nueva arriba.

    `historial` es la lista que arma `agregar` (la más vieja primero, como pasó).
    """
    # El título NO lleva el conteo: si el texto del título cambia, Streamlit lo trata
    # como un expander nuevo y lo vuelve a cerrar en cada clic.
    with st.expander("Historial de cambios", expanded=False):
        if not historial:
            st.caption("Todavía no hay cambios. Mueva una palanca para empezar.")
            return
        st.caption(f"{len(historial)} cambios · el más reciente arriba")
        # reversed(...) invierte el orden solo para mostrar: la lista no cambia.
        for numero, entrada in zip(range(len(historial), 0, -1), reversed(historial)):
            st.markdown(f"**{numero}. {_sin_latex(entrada['cambio'])}**")
            st.markdown(_sin_latex(entrada["texto"]))
            detalle = f"{entrada['n']} empresas · señal {entrada['senal']}"
            if entrada.get("completado"):
                detalle += " · grupo completado"
            detalle += f" · fuente: {ICONO_FUENTE.get(entrada['fuente'], entrada['fuente'])}"
            st.caption(detalle)
            if numero > 1:
                st.divider()