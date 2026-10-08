"""Streaming, límite de 4 s y respaldo. Dueño: Julian."""
import os
import queue
import threading

import anthropic

import config
from ia.plantilla import plantilla
from ia.prompts import PROMPT_SISTEMA, armar_mensaje

PAUSA_MAX_SEG = 10  # máximo entre un trozo y el siguiente, ya empezado el texto
_FIN = object()  # marca que el flujo terminó bien


def _cliente_real():
    """Cliente de Anthropic. La llave sale del entorno o de .streamlit/secrets.toml."""
    llave = os.environ.get("ANTHROPIC_API_KEY")
    if not llave:
        import streamlit as st  # solo aquí, para que las pruebas no lo necesiten

        llave = st.secrets["ANTHROPIC_API_KEY"]
    # max_retries=0: si falla, caemos a la plantilla de inmediato en vez de reintentar
    return anthropic.Anthropic(api_key=llave, max_retries=0, timeout=config.TIEMPO_LIMITE_IA_SEG * 2)


def _leer_flujo(cliente, estado, anterior, cola, cancelar):
    """Corre en un hilo: pide el texto a la API y lo va dejando en la cola."""
    try:
        cliente = cliente or _cliente_real()
        with cliente.messages.stream(
            model=config.MODELO_IA,
            max_tokens=300,
            system=PROMPT_SISTEMA,
            messages=[{"role": "user", "content": armar_mensaje(estado, anterior)}],
        ) as flujo:
            for trozo in flujo.text_stream:
                if cancelar.is_set():
                    return
                cola.put(trozo)
        cola.put(_FIN)
    except Exception as error:  # noqa: BLE001  cualquier fallo (sin llave, sin internet, API caída)
        cola.put(error)


def explicar(estado, anterior, cliente=None, limite=None):
    """Generador de texto para st.write_stream.

    Si la primera palabra no llega en `limite` segundos, o hay cualquier error,
    devuelve de un golpe plantilla(estado). Al terminar guarda la fuente y el
    texto final en estado["explicacion"].
    """
    limite = config.TIEMPO_LIMITE_IA_SEG if limite is None else limite
    cola = queue.Queue()
    cancelar = threading.Event()
    hilo = threading.Thread(target=_leer_flujo, args=(cliente, estado, anterior, cola, cancelar), daemon=True)
    hilo.start()

    trozos = []
    try:
        while True:
            espera = limite if not trozos else PAUSA_MAX_SEG
            try:
                item = cola.get(timeout=espera)
            except queue.Empty:
                raise TimeoutError("la IA tardó demasiado") from None
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
    except GeneratorExit:  # llegó un clic nuevo y nadie sigue leyendo este texto
        cancelar.set()
        raise
    except Exception:  # noqa: BLE001  cualquier fallo cae a la plantilla
        cancelar.set()
        texto = plantilla(estado)
        estado["explicacion"] = {"fuente": "plantilla", "texto": texto}
        if not trozos:  # si ya se escribió algo en pantalla, no se puede borrar desde aquí
            yield texto
