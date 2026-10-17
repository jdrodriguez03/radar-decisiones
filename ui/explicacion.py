"""Panel derecho: explicación de la IA, señal y n. Dueño: Julian."""
import itertools

import streamlit as st

from ia.cache import firma
from ia.explicar import explicar

ESPERA = "Analizando las empresas…"
AVISO_PENDIENTE = "Las cifras cambiaron. Pulse **Explicar** para ver qué muestran las empresas que ya aplican esta combinación."


def sin_latex(texto):
    """Streamlit lee $...$ como fórmula: "$6.3 millones ... $2.3" saldría en cursiva matemática."""
    return texto.replace("$", r"\$")


def _sin_latex_stream(generador):
    for trozo in generador:
        yield sin_latex(trozo)


def pie(estado):
    """La línea bajo la explicación: qué tan clara es la señal y contra cuántas empresas se compara."""
    grupo = estado.get("grupo") or {}
    n = grupo.get("n", 0)
    etiqueta = (estado.get("senal") or {}).get("etiqueta")
    if etiqueta in (None, "no aplica"):  # estado inicial: no hay grupo contra resto
        return f"Comparado con las {n} empresas de la encuesta"
    texto = f"Señal {etiqueta} · {n} empresas que ya lo hacen"
    if grupo.get("completado"):
        texto += " · grupo completado con empresas similares"
    return texto


def render(contenedor, estado, anterior, cliente=None, cache=None):
    """Dibuja el panel derecho: la explicación con efecto de escritura y, debajo, la señal y el n.

    Mientras el texto se consigue y se valida, se ve ESPERA. El texto solo aparece cuando
    ya está aprobado, así que en pantalla nunca hay una cifra que no esté en los datos.
    `cliente` y `cache` son opcionales: el sandbox los usa para simular cada caso del flujo.
    """
    with contenedor:
        caja = st.empty()  # un solo lugar: primero el mensaje de espera, después el texto
        pulso = st.empty()  # marcador invisible: tocarlo deja que Streamlit note un clic nuevo
        caja.caption(ESPERA)
        texto = explicar(estado, anterior, cliente=cliente, cache=cache, latido=pulso.empty)
        primera = next(texto, None)  # aquí se espera: la IA escribe en silencio y se valida
        if primera is not None:
            with caja.container():
                st.write_stream(_sin_latex_stream(itertools.chain([primera], texto)))
        st.caption(pie(estado))


# --- Botón Explicar: qué se ve entre una pulsación y la siguiente ---

def falta_explicar(estado, explicado):
    """True si lo que hay en pantalla no es lo último que se explicó.

    `explicado` es el estado que se explicó al pulsar Explicar (None si aún no se pulsa).
    Compara empresa, palancas movidas y costo por baja: lo mismo que distingue dos
    explicaciones en el caché. Mover un control y regresarlo cuenta como "sin cambios".
    """
    return explicado is None or firma(estado) != firma(explicado)


def aviso_pendiente(contenedor):
    """Dibuja el aviso de que falta pulsar Explicar. Se llama EN LUGAR del texto viejo.

    El texto viejo no se muestra: si dice "22 empresas" mientras la pantalla ya dice 5,
    el jurado vería una contradicción. Mejor un aviso que un texto equivocado.
    """
    with contenedor:
        st.info(AVISO_PENDIENTE)


def mostrar(contenedor, estado):
    """Vuelve a dibujar la explicación ya escrita, sin llamar a la IA.

    Streamlit redibuja la página con cualquier clic. Si nada cambió desde la última
    explicación, el texto se muestra tal cual (de estado["explicacion"]) con su pie.
    """
    with contenedor:
        st.markdown(sin_latex((estado.get("explicacion") or {}).get("texto", "")))
        st.caption(pie(estado))
