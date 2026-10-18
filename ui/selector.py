"""Empresas de demo y 'Mi empresa'. Dueño: Juanes.

render(empresas) dibuja el selector y devuelve el PERFIL de la empresa elegida,
con la misma forma que el bloque "empresa" del contrato:

    {
        "id": "COMPAÑIA 36",
        "plantilla_op": 1438,
        "palancas": {"sal_dia_ini": 323.61, "aguinaldo_op": 15, ...},
        "indicadores": {"rot_anual": 0.516, "rot_temprana": 0.40, "ausentismo": 0.015},
    }

En "Mi empresa" los indicadores que no se capturan (rot_temprana y ausentismo)
van como None. Si el usuario todavía no envía el formulario, render devuelve None.

En "Empresas de demo" las palancas sin dato en la encuesta no aparecen en "palancas"
(ver perfil_demo).

Las funciones perfil_demo, perfil_mi_empresa, validar_captura, ids_ordenados y
palancas_sin_dato no usan Streamlit, así que se pueden probar con pytest.
"""

from __future__ import annotations

import math
import re

import pandas as pd
import streamlit as st

from config import PALANCAS

# Empresas del guion, en este orden, arriba de la lista.
RECOMENDADAS = ["COMPAÑIA 36", "COMPAÑIA 29", "COMPAÑIA 15"]

# Id fijo para la empresa capturada a mano (no existe entre las 40).
MI_EMPRESA_ID = "MI EMPRESA"

ETIQUETAS = {
    "sal_dia_ini": "Salario diario inicial ($)",
    "aguinaldo_op": "Días de aguinaldo",
    "prima_vac_op": "Prima vacacional (%)",
    "vales_op": "Vales de despensa (% del salario)",
    "rutas_x100": "Rutas por cada 100 operativos",
}

# Nombre en el contrato -> columna en empresas.parquet.
COL_INDICADORES = {
    "rot_anual": "rot_anual",
    "rot_temprana": "bajas_menos3m",
    "ausentismo": "aus_inj_op",
}

# Rangos válidos de los dos campos que no son palancas.
RANGO_PLANTILLA = (10, 20_000)  # operativos
RANGO_ROT_MENSUAL = (0.0, 25.0)  # % mensual (52% anual = 4.3% mensual)

_K = "d_selector_"  # prefijo de las llaves de st.session_state


# ── Funciones sin Streamlit (se prueban con pytest) ─────────────────────────


def _es_proporcion(col: str) -> bool:
    """Prima y vales se guardan como proporción (0.25); en pantalla van en %."""
    return PALANCAS[col][1] <= 1.0


def _numero(valor) -> float | None:
    if valor is None:
        return None
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(valor) else valor


def _formato(col: str, valor: float) -> str:
    if _es_proporcion(col):
        return f"{valor * 100:g}%"
    if col == "sal_dia_ini":
        return f"${valor:,.0f}"
    return f"{valor:g}"


def _tabla(empresas: pd.DataFrame) -> pd.DataFrame:
    """Devuelve la tabla con el id de empresa como índice."""
    if "empresa" in empresas.columns:
        return empresas.set_index("empresa")
    return empresas


def _orden_natural(empresa_id) -> tuple:
    m = re.search(r"\d+", str(empresa_id))
    return (int(m.group()) if m else 10**9, str(empresa_id))


def ids_ordenados(empresas: pd.DataFrame) -> list[str]:
    """Recomendadas primero (en el orden del guion) y luego COMPAÑIA 1, 2, 3..."""
    ids = [str(i) for i in _tabla(empresas).index]
    arriba = [i for i in RECOMENDADAS if i in ids]
    resto = sorted((i for i in ids if i not in RECOMENDADAS), key=_orden_natural)
    return arriba + resto


def perfil_demo(empresas: pd.DataFrame, empresa_id: str) -> dict:
    """Perfil de una de las 40 empresas, leído de empresas.parquet.

    Las palancas sin dato en la encuesta NO se incluyen en "palancas", porque el
    contrato (Empresa.palancas: dict[str, float]) no acepta None. Hoy pasa con
    COMPAÑIA 27 (sin ninguna) y con COMPAÑIA 10, 11 y 35 (sin vales).
    """
    fila = _tabla(empresas).loc[empresa_id]
    plantilla = _numero(fila.get("plantilla_op"))
    palancas = {col: _numero(fila.get(col)) for col in PALANCAS}
    return {
        "id": str(empresa_id),
        "plantilla_op": None if plantilla is None else round(plantilla),
        "palancas": {col: v for col, v in palancas.items() if v is not None},
        "indicadores": {k: _numero(fila.get(c)) for k, c in COL_INDICADORES.items()},
    }


def palancas_sin_dato(perfil: dict) -> list[str]:
    """Palancas que la empresa no reportó (no vienen en perfil["palancas"])."""
    return [col for col in PALANCAS if col not in perfil["palancas"]]


def validar_captura(datos: dict) -> list[str]:
    """Revisa el formulario de "Mi empresa". Devuelve la lista de errores (vacía si todo bien).

    datos = {"plantilla_op": 800, "rot_mensual_pct": 4.3,
             "palancas": {"sal_dia_ini": 300, "prima_vac_op": 0.25, ...}}
    Las palancas van en las mismas unidades que la base (prima 0.25, no 25).
    """
    errores = []

    lo, hi = RANGO_PLANTILLA
    p = _numero(datos.get("plantilla_op"))
    if p is None or not lo <= p <= hi:
        errores.append(f"Plantilla operativa: escriba un número entre {lo:,} y {hi:,} operativos.")

    lo, hi = RANGO_ROT_MENSUAL
    r = _numero(datos.get("rot_mensual_pct"))
    if r is None or not lo <= r <= hi:
        errores.append(
            f"Rotación mensual: escriba un porcentaje entre {lo:g}% y {hi:g}% "
            "(por ejemplo 4.3 si pierde 4.3% de sus operativos al mes)."
        )

    palancas = datos.get("palancas", {})
    for col, (minimo, maximo, _paso) in PALANCAS.items():
        v = _numero(palancas.get(col))
        tolerancia = 1e-9  # 12.0 / 100 puede quedar como 0.12000000000000001
        if v is None or not minimo - tolerancia <= v <= maximo + tolerancia:
            errores.append(
                f"{ETIQUETAS.get(col, col)}: debe estar entre {_formato(col, minimo)} y "
                f"{_formato(col, maximo)}, el rango de las empresas de la encuesta."
            )
    return errores


def perfil_mi_empresa(datos: dict) -> dict:
    """Arma el perfil de una empresa capturada a mano. Lanza ValueError si hay errores."""
    errores = validar_captura(datos)
    if errores:
        raise ValueError("; ".join(errores))
    return {
        "id": MI_EMPRESA_ID,
        "plantilla_op": round(datos["plantilla_op"]),
        "palancas": {col: float(datos["palancas"][col]) for col in PALANCAS},
        "indicadores": {
            "rot_anual": round(float(datos["rot_mensual_pct"]) / 100 * 12, 4),
            "rot_temprana": None,
            "ausentismo": None,
        },
    }


def _valor_inicial(empresas: pd.DataFrame, col: str) -> float:
    """Mediana de las 40, ajustada al paso y dentro del rango del control."""
    minimo, maximo, paso = PALANCAS[col]
    mediana = _numero(empresas[col].median()) if col in empresas.columns else None
    if mediana is None:
        mediana = (minimo + maximo) / 2
    ajustado = minimo + round((mediana - minimo) / paso) * paso
    return float(min(max(ajustado, minimo), maximo))


# ── Pantalla ────────────────────────────────────────────────────────────────


def render(empresas: pd.DataFrame) -> dict | None:
    """Dibuja el selector y devuelve el perfil elegido (None si "Mi empresa" aún no se envía)."""
    modo = st.radio(
        "Empresa a analizar",
        ["Empresas de demo", "Mi empresa"],
        horizontal=True,
        key=_K + "modo",
    )
    if modo == "Empresas de demo":
        return _render_demo(empresas)
    return _render_mi_empresa(empresas)


def _render_demo(empresas: pd.DataFrame) -> dict:
    def etiqueta(empresa_id: str) -> str:
        return f"⭐ {empresa_id} · recomendada" if empresa_id in RECOMENDADAS else empresa_id

    empresa_id = st.selectbox(
        "Empresa",
        ids_ordenados(empresas),
        format_func=etiqueta,
        key=_K + "demo",
    )
    perfil = perfil_demo(empresas, empresa_id)
    if perfil["plantilla_op"] is not None:
        st.caption(f"{perfil['plantilla_op']:,} operativos")
    faltan = palancas_sin_dato(perfil)
    if faltan:
        nombres = ", ".join(ETIQUETAS.get(c, c).lower() for c in faltan)
        st.caption(f"Sin dato en la encuesta: {nombres}.")
    return perfil


def _render_mi_empresa(empresas: pd.DataFrame) -> dict | None:
    st.caption("Capture los datos de su planta. Las palancas usan el rango de las 40 empresas de la encuesta.")

    with st.container(border=True): #CAMBIEEEEEEEEEEEEEEEEEEEEEEEE
        plantilla = st.number_input(
            "Plantilla operativa (personas)", min_value=0, value=500, step=10, key=_K + "plantilla"
        )
        rot_mensual = st.number_input(
            "Rotación mensual (%)", min_value=0.0, value=3.0, step=0.1, format="%.1f", key=_K + "rot"
        )

        capturadas = {}
        for col, (minimo, maximo, paso) in PALANCAS.items():
            inicial = _valor_inicial(empresas, col)
            ayuda = f"Rango de la encuesta: {_formato(col, minimo)} a {_formato(col, maximo)}"
            if _es_proporcion(col):
                valor = st.number_input(
                    ETIQUETAS.get(col, col),
                    value=float(inicial * 100),
                    step=float(paso * 100),
                    format="%.1f",
                    help=ayuda,
                    key=_K + col,
                )
                capturadas[col] = valor / 100
            else:
                valor = st.number_input(
                    ETIQUETAS.get(col, col),
                    value=float(inicial),
                    step=float(paso),
                    help=ayuda,
                    key=_K + col,
                )
                capturadas[col] = valor
        enviado = st.button("Usar mi empresa", key=_K + "usar") ##CAMBIEEEEEEEEEEEEEEE

    if enviado:
        datos = {"plantilla_op": plantilla, "rot_mensual_pct": rot_mensual, "palancas": capturadas}
        errores = validar_captura(datos)
        if errores:
            for e in errores:
                st.error(e)
            st.session_state.pop(_K + "perfil_mi", None)
        else:
            st.session_state[_K + "perfil_mi"] = perfil_mi_empresa(datos)

    perfil = st.session_state.get(_K + "perfil_mi")
    if perfil is None:
        st.info('Llene los 7 campos y presione "Usar mi empresa".')
    else:
        return perfil
