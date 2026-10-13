"""Sandbox de Julian: el panel derecho tal como lo verá el público, con cada caso del flujo.

Correr desde la raíz del repo:  streamlit run sandbox/c_panel.py

Arriba se elige el paso del guion y un escenario (con caché, sin internet, IA que inventa…).
El panel se dibuja con ui.explicacion.render, igual que en la app. Debajo, "Detrás de escena"
dice qué capa respondió (caché, IA validada o plantilla) y por qué.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para poder importar config, ia y ui

import anthropic
import streamlit as st

import config
from ia.cache import buscar, cargar, llave
from ia.derivadas import cifras_derivadas
from ia.explicar import _cliente_real
from ia.prompts import anterior_util, armar_mensaje
from ia.validador import cifras_inventadas
from ui.explicacion import render

# El guion en orden: cada paso llega desde el anterior de la lista (como en la demo).
GUION = [
    ("Inicio · COMPAÑIA 36 sin cambios", "05_inicial"),
    ("Paso 1 · Aguinaldo 15 → 20 días", "01_aguinaldo"),
    ("Paso 2 · + Prima vacacional 25% → 50%", "02_prima"),
    ("Paso 3 · + Salario inicial → $350", "03_salario"),
    ("Otra empresa · COMPAÑIA 37, vales a 12%", "04_ya_rota_menos"),
]

FUENTES = {
    "cache": "① Caché: texto precalculado y revisado",
    "llm": "② IA en vivo: escribió, pasó el validador y se mostró",
    "plantilla": "③ Plantilla: la IA no pudo dar un texto válido",
}


# --- Clientes falsos para provocar cada caso sin depender de la API ---

class _Flujo:
    """Imita lo que devuelve cliente.messages.stream(...)."""

    def __init__(self, texto="", espera=0.0, error=None):
        self.texto, self.espera, self.error = texto, espera, error

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def close(self):
        pass

    @property
    def text_stream(self):
        time.sleep(self.espera)
        if self.error:
            raise self.error
        yield from (palabra + " " for palabra in self.texto.split())


class _Cliente:
    def __init__(self, **datos):
        self.messages, self.datos = self, datos

    def stream(self, **kwargs):
        return _Flujo(**self.datos)


def sin_internet():
    return _Cliente(error=anthropic.APIConnectionError(request=None))


def ia_que_inventa(estado):
    n = estado["grupo"]["n"]
    return _Cliente(texto=f"Esas {n} empresas pierden 31 puntos menos de su plantilla al año que las demás.")


def ia_lenta():
    return _Cliente(texto="Este texto llega tarde y no debería verse.", espera=6)


class Grabador:
    """Envuelve un cliente (el real o uno falso) y guarda lo que la IA escribió, aunque se rechace."""

    def __init__(self, base=None):
        self.base, self.messages, self.texto = base, self, ""

    def stream(self, **kwargs):
        base = self.base or _cliente_real()  # el real se crea aquí: si no hay llave, explicar cae a la plantilla
        return _FlujoGrabado(base.messages.stream(**kwargs), self)


class _FlujoGrabado:
    def __init__(self, gestor, grabador):
        self.gestor, self.grabador, self.flujo = gestor, grabador, None

    def __enter__(self):
        self.flujo = self.gestor.__enter__()
        return self

    def __exit__(self, *args):
        return self.gestor.__exit__(*args)

    def close(self):
        if self.flujo is not None and hasattr(self.flujo, "close"):
            self.flujo.close()

    @property
    def text_stream(self):
        for trozo in self.flujo.text_stream:
            self.grabador.texto += trozo
            yield trozo


ESCENARIOS = {
    "Como en la demo": (
        lambda e: None, None,
        "Busca en el caché; si el paso no está, le pide el texto a la IA real y lo valida; si falla, plantilla.",
    ),
    "IA en vivo (sin caché)": (
        lambda e: None, {},
        "Ignora el caché: siempre le pide el texto a la IA real (necesita la llave y gasta crédito).",
    ),
    "Sin internet, con caché": (
        lambda e: sin_internet(), None,
        "El wifi del evento falla: los pasos guardados siguen saliendo del caché; los demás, de la plantilla.",
    ),
    "Sin internet ni caché": (
        lambda e: sin_internet(), {},
        "Lo peor que puede pasar: sin internet y sin texto guardado. Sale la plantilla.",
    ),
    "IA que inventa una cifra": (
        ia_que_inventa, {},
        "La IA escribe '31 puntos', que no está en los datos. El validador la rechaza antes de mostrarla.",
    ),
    "IA lenta (más de 4 s)": (
        lambda e: ia_lenta(), {},
        f"La primera palabra no llega en {config.TIEMPO_LIMITE_IA_SEG} s. Sale la plantilla sin esperar más.",
    ),
}


def cargar_fixture(nombre):
    return json.loads((config.RUTA_FIXTURES / f"{nombre}.json").read_text(encoding="utf-8"))


st.set_page_config(page_title="Sandbox · panel de explicación", layout="wide")
st.title("Sandbox · panel de explicación")
st.caption("Lo que ve el público en la columna derecha, y qué pasa detrás en cada caso.")

col_control, col_panel = st.columns([1, 1.4])

with col_control:
    nombres = [n for n, _ in GUION]
    paso = st.selectbox("Paso del guion", nombres, index=1)
    i = nombres.index(paso)
    estado = cargar_fixture(GUION[i][1])
    previo = cargar_fixture(GUION[i - 1][1]) if i > 0 else None
    sin_anterior = st.checkbox(
        "Llegar a este paso sin pasar por el anterior",
        help="Como si un juez llegara por otro camino: el caché usa el texto sin 'antes…'.",
    )
    anterior = None if sin_anterior else previo

    escenario = st.radio("Escenario", list(ESCENARIOS))
    fabrica, cache, descripcion = ESCENARIOS[escenario]
    st.info(descripcion)
    mover = st.button("Mover la palanca", type="primary", use_container_width=True)

with col_panel:
    st.subheader("Lo que ve el público")
    panel = st.container(border=True)
    if not mover:
        panel.caption("Elige un paso y un escenario, y pulsa «Mover la palanca».")
    else:
        grabador = Grabador(fabrica(estado))
        inicio = time.perf_counter()
        render(panel, estado, anterior, cliente=grabador, cache=cache)
        total = time.perf_counter() - inicio

        st.subheader("Detrás de escena")
        fuente = estado["explicacion"]["fuente"]
        for clave, etiqueta in FUENTES.items():
            st.markdown(f"**✅ {etiqueta}**" if clave == fuente else f"<span style='opacity:.45'>{etiqueta}</span>",
                        unsafe_allow_html=True)

        m1, m2 = st.columns(2)
        m1.metric("Del clic al texto completo", f"{total:.2f} s")
        m2.metric("Efecto de escritura", f"{config.PAUSA_ESCRITURA_SEG * 1000:.0f} ms por palabra")

        cache_real = cargar() if cache is None else cache
        clave = llave(estado, anterior)
        con_anterior = anterior_util(estado, anterior) is not None
        st.markdown("**Caché**")
        st.code(clave, language="text")
        if cache == {}:
            st.write("Este escenario ignora el caché a propósito.")
        elif buscar(estado, anterior, cache_real):
            exacta = clave in cache_real
            st.write("Estaba guardado " + ("con su paso anterior." if exacta and con_anterior else "y pasó el validador."))
        else:
            st.write("No estaba guardado: se le pidió el texto a la IA.")

        if grabador.texto:
            st.markdown("**Lo que escribió la IA (antes de validar)**")
            st.code(grabador.texto.strip(), language="text")
            inventadas = cifras_inventadas(grabador.texto, estado, anterior)
            if inventadas:
                st.error(f"Rechazado: cifras que no están en los datos → {', '.join(f'{c:g}' for c in inventadas)}")
            elif fuente == "llm":
                st.success("Todas sus cifras están en los datos: se mostró.")

        with st.expander("Métricas precalculadas que la IA puede usar"):
            derivadas = cifras_derivadas(estado)
            if derivadas:
                st.table([{"Métrica": d["que_es"], "Valor": d["valor"]} for d in derivadas.values()])
            else:
                st.write("Ninguna aplica a este estado.")
        with st.expander("Mensaje exacto que recibe la IA"):
            st.code(armar_mensaje(estado, anterior), language="text")
