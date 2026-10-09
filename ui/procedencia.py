
"""Etiquetas observado / calculado / supuesto. Dueño: Juanes.

Cada función recibe un texto y lo devuelve como HTML con el color de su procedencia.
Para mostrarlo:  st.markdown(observado("22 empresas"), unsafe_allow_html=True)
"""
from html import escape

from ui import tema

# Mientras Gaby no los defina en ui/tema.py, se usan estos de respaldo.
ACENTO = getattr(tema, "ACENTO", "#4FB3BF")
GRIS = getattr(tema, "GRIS", "#9AA0A6")
AMBAR = getattr(tema, "AMBAR", "#F5A524")


def _pintar(texto, color):
    return f'<span style="color:{color}">{escape(str(texto))}</span>'


def observado(texto):
    """Dato que sale directo de la base (medianas, n, percentiles). Color de acento."""
    return _pintar(texto, ACENTO)


def calculado(texto):
    """Aritmética sobre lo observado y el perfil (los costos). Gris."""
    return _pintar(texto, GRIS)


def supuesto(texto):
    """Valor editable por el directivo (costo por baja, costo por ruta). Ámbar."""
    return _pintar(texto, AMBAR)
