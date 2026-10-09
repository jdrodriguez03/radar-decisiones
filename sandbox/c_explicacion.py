"""Sandbox de Julian: prueba la explicación de la IA con los fixtures del guion.

Correr desde la raíz del repo:  streamlit run sandbox/c_explicacion.py
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para poder importar config e ia

import streamlit as st

import config
from ia.explicar import explicar
from ia.plantilla import plantilla
from ia.prompts import armar_mensaje

# Pasos del guion: nombre visible -> (fixture actual, fixture del paso anterior)
PASOS = {
    "01 · Aguinaldo 15 → 20": ("01_aguinaldo", "05_inicial"),
    "02 · + Prima 25% → 50%": ("02_prima", "01_aguinaldo"),
    "03 · + Salario → $350": ("03_salario", "02_prima"),
    "04 · Vales (ya pierde menos)": ("04_ya_rota_menos", "05_inicial"),
    "05 · Estado inicial": ("05_inicial", None),
}
MODELOS = [config.MODELO_IA, "claude-haiku-5-5", "claude-sonnet-5-5"]  # el primero es el de config.py
PALABRAS_PROHIBIDAS = [
    "logrará", "reducirá", "reduce", "disminuye","promedio", "pasaría a", "obtendrá", "grupo de comparación", "brecha", "rotación",
    "rotar como ese grupo", "sector", "$0.0",
]


def cargar(nombre):
    return json.loads((config.RUTA_FIXTURES / f"{nombre}.json").read_text(encoding="utf-8"))


def stream_simulado(estado, pausa=0.04):
    """Escribe la plantilla palabra por palabra, sin API."""
    for palabra in plantilla(estado).split(" "):
        yield palabra + " "
        time.sleep(pausa)


class FlujoLento:
    """Imita una API que tarda 6 s en dar la primera palabra."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    @property
    def text_stream(self):
        time.sleep(6)
        yield "Este texto llega tarde y no debería verse."


class ClienteLento:
    def __init__(self):
        self.messages = self

    def stream(self, **kwargs):
        return FlujoLento()


def con_tiempos(generador, tiempos):
    """Anota cuándo llegó la primera palabra y cuándo terminó el texto."""
    inicio = time.perf_counter()
    for trozo in generador:
        if "primera" not in tiempos:
            tiempos["primera"] = time.perf_counter() - inicio
        yield trozo
    tiempos["total"] = time.perf_counter() - inicio


def sin_latex(generador):
    """Streamlit lee $...$ como fórmula: se escapa cada $ para que se vea como pesos."""
    for trozo in generador:
        yield trozo.replace("$", r"\$")


def revision_rapida(texto, estado):
    """Lo que se puede revisar a simple vista: oraciones, palabras, palabras prohibidas y el n."""
    oraciones = [o for o in re.split(r"(?<=[.!?])\s+", texto.strip()) if o]
    prohibidas = [p for p in PALABRAS_PROHIBIDAS if p in texto.lower()]
    n = str(estado["grupo"]["n"])
    return [
        ("Oraciones (máx. 3)", len(oraciones), len(oraciones) <= 3),
        ("Palabras (máx. 75)", len(texto.split()), len(texto.split()) <= 75),
        ("Menciona el n del grupo", n, n in texto),
        ("Palabras prohibidas", ", ".join(prohibidas) or "ninguna", not prohibidas),
    ]


st.set_page_config(page_title="Sandbox · explicación IA", layout="wide")
st.title("Sandbox · explicación de la IA")

col_estado, col_ia = st.columns(2)
with col_estado:
    paso = st.selectbox("Paso del guion", list(PASOS))
    actual, previo = PASOS[paso]
    usar_anterior = st.checkbox("Comparar con el paso anterior", value=previo is not None, disabled=previo is None)
    estado = cargar(actual)
    anterior = cargar(previo) if previo and usar_anterior else None

    cambio = estado["cambio"]
    st.caption(
        f"{estado['empresa']['id']} · "
        + (f"{cambio['palanca']} {cambio['de']} → {cambio['a']}" if cambio else "sin cambios")
        + (f" · paso anterior: {previo}" if anterior else " · sin paso anterior")
    )
    with st.expander("Mensaje exacto que recibe la IA"):
        st.code(armar_mensaje(estado, anterior), language="text")

with col_ia:
    modo = st.radio(
        "Fuente del texto",
        ["API real", "API lenta (prueba del límite)", "Simulado (plantilla)"],
        horizontal=True,
    )
    modelo = st.selectbox("Modelo", list(dict.fromkeys(MODELOS)), disabled=modo != "API real")
    st.subheader(f"Respuesta de {modelo}" if modo == "API real" else "Respuesta")
    if st.button("Generar explicación", type="primary"):
        if modo == "Simulado (plantilla)":
            generador = stream_simulado(estado)
        else:
            cliente = ClienteLento() if modo.startswith("API lenta") else None
            pulso = st.empty()  # marcador invisible: tocarlo deja que Streamlit note un clic nuevo
            generador = explicar(estado, anterior, cliente=cliente, latido=pulso.empty, modelo=modelo)
        tiempos = {}
        st.write_stream(sin_latex(con_tiempos(generador, tiempos)))
        fuente = estado["explicacion"]["fuente"] if modo != "Simulado (plantilla)" else "simulado"
        m1, m2, m3 = st.columns(3)
        m1.metric("Primera palabra", f"{tiempos.get('primera', 0):.2f} s")
        m2.metric("Texto completo", f"{tiempos.get('total', 0):.2f} s")
        m3.metric("Fuente usada", fuente)

        texto = estado["explicacion"]["texto"] if modo != "Simulado (plantilla)" else plantilla(estado)
        st.markdown("**Revisión rápida**")
        for regla, valor, cumple in revision_rapida(texto, estado):
            st.write(f"{'✅' if cumple else '❌'} {regla}: {valor}")
        st.caption("Para docs/pruebas_ia.md, copia el texto de abajo:")
        st.code(texto, language="text")