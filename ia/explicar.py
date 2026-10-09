"""Streaming, límite de 4 s y respaldo. Dueño: Julian."""
import contextlib
import os
import queue
import threading
import time

import anthropic

import config
from ia.plantilla import plantilla
from ia.prompts import PROMPT_SISTEMA, armar_mensaje

PAUSA_MAX_SEG = 10  # máximo entre un trozo y el siguiente, ya empezado el texto
LATIDO_SEG = 0.1  # cada cuánto se avisa a la pantalla mientras se espera, para notar un clic nuevo
_FIN = object()  # marca que el flujo terminó bien


def _cliente_real():
    """Cliente de Anthropic. La llave sale del entorno o de .streamlit/secrets.toml."""
    llave = os.environ.get("ANTHROPIC_API_KEY")
    if not llave:
        import streamlit as st  # solo aquí, para que las pruebas no lo necesiten

        llave = st.secrets["ANTHROPIC_API_KEY"]
    # max_retries=0: si falla, caemos a la plantilla de inmediato en vez de reintentar
    return anthropic.Anthropic(api_key=llave, max_retries=0, timeout=config.TIEMPO_LIMITE_IA_SEG * 2)


def _leer_flujo(cliente, estado, anterior, cola, cancelar, abierto):
    """Corre en un hilo: pide el texto a la API y lo va dejando en la cola."""
    try:
        cliente = cliente or _cliente_real()
        with cliente.messages.stream(
            model=config.MODELO_IA,
            max_tokens=300,
            system=PROMPT_SISTEMA,
            messages=[{"role": "user", "content": armar_mensaje(estado, anterior)}],
        ) as flujo:
            abierto["flujo"] = flujo  # se guarda para poder cerrarlo desde afuera
            if cancelar.is_set():  # el clic nuevo llegó mientras se abría la conexión
                return
            for trozo in flujo.text_stream:
                if cancelar.is_set():
                    return
                cola.put(trozo)
        cola.put(_FIN)
    except Exception as error:  # noqa: BLE001  cualquier fallo (sin llave, sin internet, API caída)
        if not cancelar.is_set():  # si ya se canceló, a nadie le importa este error
            cola.put(error)


def _detener(cancelar, abierto):
    """Avisa al hilo que pare y cierra la conexión con la API, si ya estaba abierta."""
    cancelar.set()
    flujo = abierto.get("flujo")
    if flujo is not None and hasattr(flujo, "close"):
        with contextlib.suppress(Exception):  # cerrar es solo limpieza: si falla, no importa
            flujo.close()


def _esperar(cola, espera, latido):
    """Espera el siguiente trozo hasta `espera` segundos.

    No espera de un solo golpe: lo hace en pedazos de LATIDO_SEG y entre pedazo y
    pedazo llama a latido(). En la app, latido toca la pantalla, y ese toque es el
    momento en que Streamlit revisa si llegó un clic nuevo y corta este texto.
    """
    fin = time.monotonic() + espera
    while True:
        restante = fin - time.monotonic()
        if restante <= 0:
            raise TimeoutError("la IA tardó demasiado")
        try:
            return cola.get(timeout=min(LATIDO_SEG, restante))
        except queue.Empty:
            if latido is not None:
                latido()


def explicar(estado, anterior, cliente=None, limite=None, latido=None):
    """Generador de texto para st.write_stream.

    Si la primera palabra no llega en `limite` segundos, o hay cualquier error,
    devuelve de un golpe plantilla(estado). Al terminar guarda la fuente y el
    texto final en estado["explicacion"].

    Si llega un clic nuevo mientras se escribe (Streamlit deja de leer este
    generador), se cierra la conexión con la API y no se toca estado["explicacion"].
    """
    limite = config.TIEMPO_LIMITE_IA_SEG if limite is None else limite
    cola = queue.Queue()
    cancelar = threading.Event()
    abierto = {}  # aquí el hilo deja el flujo abierto, para poder cerrarlo
    hilo = threading.Thread(
        target=_leer_flujo, args=(cliente, estado, anterior, cola, cancelar, abierto), daemon=True
    )
    hilo.start()

    trozos = []
    try:
        while True:
            item = _esperar(cola, limite if not trozos else PAUSA_MAX_SEG, latido)
            if item is _FIN:
                break
            if isinstance(item, Exception):
                raise item
            trozos.append(item)
            yield item
        texto = "".join(trozos).strip()
        if not texto:
            raise ValueError("la IA devolvió un texto vacío")
        estado["explicacion"] = {"fuente": "llm", "texto": texto}
    except Exception:  # noqa: BLE001  cualquier fallo cae a la plantilla
        _detener(cancelar, abierto)
        texto = plantilla(estado)
        estado["explicacion"] = {"fuente": "plantilla", "texto": texto}
        if not trozos:  # si ya se escribió algo en pantalla, no se puede borrar desde aquí
            yield texto
    finally:
        # Siempre se suelta la API: al terminar bien, al caer a la plantilla
        # o porque llegó un clic nuevo y nadie sigue leyendo este texto.
        _detener(cancelar, abierto)