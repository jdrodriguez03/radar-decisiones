"""La explicación de la IA: caché, IA validada o plantilla, y el efecto de escritura. Dueño: Julian."""
import contextlib
import os
import queue
import re
import threading
import time

import anthropic

import config
from ia.cache import buscar
from ia.plantilla import plantilla
from ia.prompts import PROMPT_SISTEMA, armar_mensaje
from ia.reglas import fallas_graves
from ia.validador import es_valido

PAUSA_MAX_SEG = 10  # máximo entre un trozo y el siguiente, ya empezado el texto
LATIDO_SEG = 0.1  # cada cuánto se avisa a la pantalla mientras se espera, para notar un clic nuevo
_FIN = object()  # marca que el flujo terminó bien
TEXTO_EMERGENCIA = "La explicación no está disponible en este momento; las cifras de la pantalla siguen siendo válidas."


def _cliente_real():
    """Cliente de Anthropic. La llave sale del entorno o de .streamlit/secrets.toml."""
    llave = os.environ.get("ANTHROPIC_API_KEY")
    if not llave:
        import streamlit as st  # solo aquí, para que las pruebas no lo necesiten

        llave = st.secrets["ANTHROPIC_API_KEY"]
    # max_retries=0: si falla, caemos a la plantilla de inmediato en vez de reintentar
    return anthropic.Anthropic(api_key=llave, max_retries=0, timeout=config.TIEMPO_LIMITE_IA_SEG * 2)


def _opciones_modelo(modelo):
    """Apaga el "pensamiento" de los modelos 5.5, que viene encendido por defecto.

    Pensar antes de escribir retrasa la primera palabra (puede pasar el límite de 4 s)
    y gasta parte de max_tokens. Para tres oraciones con cifras ya calculadas no hace falta.
    Cada modelo lo apaga distinto: Sonnet 5.5 da error 400 con "disabled".
    """
    if modelo.startswith("claude-sonnet-5"):
        return {"thinking": {"type": "between_tools"}}
    if modelo.startswith("claude-haiku-5"):
        return {"thinking": {"type": "disabled"}}
    return {}  # Haiku 4.5 y anteriores no piensan si no se les pide


def _leer_flujo(cliente, estado, anterior, cola, cancelar, abierto, modelo):
    """Corre en un hilo: pide el texto a la API y lo va dejando en la cola."""
    try:
        cliente = cliente or _cliente_real()
        with cliente.messages.stream(
        model=modelo,
        max_tokens=300,
        system=PROMPT_SISTEMA,
        messages=[{"role": "user", "content": armar_mensaje(estado, anterior)}],
         **_opciones_modelo(modelo),
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


def _plantilla_segura(estado):
    """La plantilla, y si hasta ella falla (un estado incompleto), un texto fijo: nunca un error en pantalla."""
    try:
        return plantilla(estado)
    except Exception:  # noqa: BLE001
        return TEXTO_EMERGENCIA


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


def _pedir_a_la_ia(estado, anterior, cliente, limite, limite_total, latido, modelo):
    """Pide el texto completo a la IA, en silencio: nada se muestra mientras llega.

    Lanza un error si la primera palabra tarda más de `limite`, si el texto completo
    tarda más de `limite_total` o si la API falla. Siempre suelta la conexión al salir.
    """
    cola = queue.Queue()
    cancelar = threading.Event()
    abierto = {}  # aquí el hilo deja el flujo abierto, para poder cerrarlo
    hilo = threading.Thread(
        target=_leer_flujo, args=(cliente, estado, anterior, cola, cancelar, abierto, modelo), daemon=True
    )
    hilo.start()
    fin_total = time.monotonic() + limite_total
    trozos = []
    try:
        while True:
            restante = fin_total - time.monotonic()
            if restante <= 0:
                raise TimeoutError("la IA no terminó el texto a tiempo")
            item = _esperar(cola, min(limite if not trozos else PAUSA_MAX_SEG, restante), latido)
            if item is _FIN:
                return "".join(trozos).strip()
            if isinstance(item, Exception):
                raise item
            trozos.append(item)
    finally:
        # Siempre se suelta la API: al terminar, al fallar o porque llegó un clic nuevo.
        _detener(cancelar, abierto)


def _texto_aprobado(estado, anterior, cliente, limite, limite_total, latido, modelo, cache):
    """El texto que se va a mostrar y de dónde salió: ("cache" | "llm" | "plantilla", texto).

    1. Caché: si el estado ya se explicó antes (y el texto sigue pasando el validador).
    2. IA en vivo: solo si responde a tiempo, todas sus cifras están en los datos y no
       insinúa causa ni olvida advertir una señal no concluyente (ia/reglas.py).
    3. Plantilla: en cualquier otro caso (sin internet, lenta, error o cifra inventada).
    """
    guardado = buscar(estado, anterior, cache)
    if guardado:
        return "cache", guardado
    try:
        texto = _pedir_a_la_ia(estado, anterior, cliente, limite, limite_total, latido, modelo)
        if not texto:
            raise ValueError("la IA devolvió un texto vacío")
        if not es_valido(texto, estado, anterior):
            raise ValueError("la IA escribió una cifra que no está en los datos")
        if fallas_graves(texto, estado):
            raise ValueError("la IA insinuó causa o no advirtió que la señal no es concluyente")
        return "llm", texto
    except Exception:  # noqa: BLE001  cualquier fallo cae a la plantilla
        return "plantilla", _plantilla_segura(estado)


def _escribir(texto, pausa):
    """El efecto de escritura: entrega el texto ya aprobado palabra por palabra."""
    for trozo in re.findall(r"\S+\s*", texto):  # cada palabra con el espacio que la sigue
        yield trozo
        if pausa:
            time.sleep(pausa)


def explicar(
    estado, anterior, cliente=None, limite=None, latido=None, modelo=None, cache=None, limite_total=None, pausa=None
):
    """Generador de texto para st.write_stream: primero se valida, después se muestra.

    La explicación sale de la primera fuente que funcione: caché, IA en vivo (si pasa el
    validador) o plantilla. Nada se muestra hasta tener el texto completo y aprobado; luego
    se entrega palabra por palabra, con `pausa` segundos entre palabras, sea cual sea la fuente.
    Mientras se espera, `latido` se llama cada LATIDO_SEG para que la pantalla note un clic nuevo.

    Al terminar de escribir guarda la fuente y el texto en estado["explicacion"]. Si llega un
    clic nuevo antes (nadie sigue leyendo este generador), no se toca estado["explicacion"].

    `cache` permite pasar uno propio ({} obliga a pedirle el texto a la IA). Los límites
    salen de config.py: TIEMPO_LIMITE_IA_SEG (primera palabra) y TIEMPO_TOTAL_IA_SEG (texto completo).
    """
    limite = config.TIEMPO_LIMITE_IA_SEG if limite is None else limite
    limite_total = config.TIEMPO_TOTAL_IA_SEG if limite_total is None else limite_total
    pausa = config.PAUSA_ESCRITURA_SEG if pausa is None else pausa
    modelo = modelo or config.MODELO_IA  # el sandbox puede probar otro modelo sin tocar config.py

    fuente, texto = _texto_aprobado(estado, anterior, cliente, limite, limite_total, latido, modelo, cache)
    yield from _escribir(texto, pausa)
    estado["explicacion"] = {"fuente": fuente, "texto": texto}
