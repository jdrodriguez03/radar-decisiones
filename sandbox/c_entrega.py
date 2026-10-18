"""Sandbox de la entrega de Julian: caché completo, revisión y semáforo, en una sola pantalla. Dueño: Julian.

Junta lo de los días 11 y 12 y el semáforo de evidencia:
  - Pestaña «Recorrer la demo»: cada paso del guion, de los respaldos y de las 20 combinaciones,
    con su semáforo y su explicación tal como saldría en la app (fuente y tiempo incluidos).
  - Pestaña «Revisión del caché»: lo mismo que scripts/revisar_cache.py, en una tabla.

Por defecto corre SIN INTERNET (como con el wifi del evento caído): no gasta crédito y deja ver
qué sale del caché y qué saldría de la plantilla. Correr desde la raíz del repo:
    streamlit run sandbox/c_entrega.py
"""
import copy
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para poder importar config, motor, ia y ui

import pandas as pd
import streamlit as st

import config
from ia.cache import cargar as cargar_cache
from ia.cache import llave
from ia.prompts import nivel
from ia.semaforo import direccion, solidez
from motor.datos import cargar as cargar_empresas
from scripts.generar_cache import SECUENCIAS, armar_secuencias, cargar_casos
from scripts.revisar_cache import SinInternet, problemas, revisar_todo
from ui import explicacion
from ui.tema import aplicar_estilos

FUENTES = {"cache": "Caché (al instante, sin internet)", "llm": "IA en vivo", "plantilla": "Plantilla de respaldo"}

st.set_page_config(layout="wide", page_title="Entrega de Julian")
aplicar_estilos()


@st.cache_data
def cargar_todo():
    """Las historias con sus pasos ya calculados por el motor real, igual que en la app.

    Devuelve (historias, secuencias): historias es {nombre: [(título del paso, estado), ...]}.
    Las 3 primeras son las de SECUENCIAS; después, cada caso de combinaciones.yaml suelto.
    """
    supuestos = json.loads(config.RUTA_SUPUESTOS.read_text(encoding="utf-8"))
    casos = cargar_casos()
    secuencias = armar_secuencias(casos, cargar_empresas(), supuestos)
    nombres = [f"Historia · {n}" for n in SECUENCIAS] + [f"Caso suelto · {cid}" for cid in casos]
    historias = {}
    for nombre, secuencia in zip(nombres, secuencias, strict=True):
        historias[nombre] = [(titulo_paso(estado), estado) for estado in secuencia]
    return historias, secuencias


def titulo_paso(estado):
    """'aguinaldo de 20 días + prima vacacional de 50%' (y el costo por baja si no es el de siempre)."""
    texto = " + ".join(nivel(p, v) for p, v in estado["palancas_movidas"].items())
    costo = estado["pesos"]["supuestos"]["costo_por_baja"]
    if costo != 15000:
        texto += f" · costo por baja ${costo:,.0f}"
    return texto


historias, secuencias = cargar_todo()

st.markdown('<div class="titulo-app">Entrega de Julian</div>', unsafe_allow_html=True)
st.caption(
    "Días 11 y 12 (caché completo y revisado) y el semáforo de evidencia. "
    "Cada paso se calcula con el motor real, igual que en la app."
)

recorrer, revision = st.tabs(["Recorrer la demo", "Revisión del caché"])

# --- Pestaña 1: recorrer la demo paso a paso ---
with recorrer:
    izq, centro, der = st.columns([1.1, 1.2, 1.6])

    with izq:
        historia = st.selectbox("Historia o caso", list(historias))
        pasos = historias[historia]
        indice = st.radio(
            "Paso", range(len(pasos)),
            format_func=lambda i: explicacion.sin_latex(f"{i + 1}. {pasos[i][0]}"),  # "$350 ... $30,000" no es fórmula
            key=f"paso_{historia}",
        )
        sin_internet = st.toggle(
            "Sin internet (como con el wifi caído)", value=True,
            help="Apagado, un paso que no esté en el caché se le pide a la IA en vivo (gasta crédito).",
        )
        estado = copy.deepcopy(pasos[indice][1])  # explicar escribe en el estado: se trabaja sobre una copia
        anterior = pasos[indice - 1][1] if indice > 0 else None  # lo último explicado en esta historia
        st.caption(f"Empresa: {estado['empresa']['id']} · {estado['empresa']['plantilla_op']:,} operativos")
        previo = pasos[indice - 1][0] if anterior else "ninguno (primera comparación)"
        st.caption(explicacion.sin_latex(f"Paso anterior explicado: {previo}"))
        st.code(llave(estado, anterior), language=None, wrap_lines=True)
        st.caption("Llave con la que la app busca este paso en el caché.")

    with centro:
        st.subheader("Semáforo de evidencia")
        explicacion.semaforo(st.container(), estado)
        dir_, sol = direccion(estado), solidez(estado)
        if dir_ and sol:
            st.caption(
                f"Señal del motor: {estado['senal']['etiqueta']} · "
                f"grupo de {estado['grupo']['n']} contra resto de {estado['resto']['n']}"
            )

    with der:
        st.subheader("Explicación")
        if st.button("Explicar", type="primary", key=f"explicar_{historia}_{indice}"):
            contenedor = st.container()
            inicio = time.perf_counter()
            explicacion.render(contenedor, estado, anterior, cliente=SinInternet() if sin_internet else None)
            segundos = time.perf_counter() - inicio
            fuente = (estado.get("explicacion") or {}).get("fuente")
            st.success(f"Fuente: {FUENTES.get(fuente, fuente)} · {segundos:.2f} s con el efecto de escritura")
        else:
            st.info("Pulse **Explicar** para ver la explicación de este paso, como en la app.")

# --- Pestaña 2: revisión del caché (lo mismo que scripts/revisar_cache.py) ---
with revision:
    filas, sobrantes = revisar_todo(secuencias, cargar_cache())
    bien = sum(1 for f in filas if not problemas(f))
    a, b, c = st.columns(3)
    a.metric("Pasos sin problemas", f"{bien} de {len(filas)}")
    b.metric("Salen del caché", sum(1 for f in filas if f["fuente"] == "cache"))
    c.metric("Más lento (sin efecto de escritura)", f"{max(f['segundos'] for f in filas) * 1000:.1f} ms")
    tabla = pd.DataFrame(
        [
            {
                "#": i,
                "Guion": "sí" if f["guion"] else "",
                "Fuente": f["fuente"],
                "ms": round(f["segundos"] * 1000, 1),
                "Palabras": f["palabras"],
                "Problemas": "; ".join(problemas(f)) or "bien",
                "Llave": f["llave"],
            }
            for i, f in enumerate(filas, 1)
        ]
    )
    st.dataframe(tabla, hide_index=True, width="stretch")
    if sobrantes:
        st.warning("Llaves del caché que ningún paso usa: " + ", ".join(sobrantes))
    with st.expander("Leer los 26 textos"):
        for i, f in enumerate(filas, 1):
            st.markdown(f"**{i}.** `{f['llave']}`")
            st.markdown(explicacion.sin_latex(f["texto"]))
