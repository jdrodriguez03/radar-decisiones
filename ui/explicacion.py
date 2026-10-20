"""Panel derecho: explicación de la IA, señal y n. Dueño: Julian."""
import hashlib
import itertools
import json

import streamlit as st

from ia.cache import firma
from ia.explicar import explicar
from ia.semaforo import NIVELES, direccion, lectura_pesos, solidez

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


# --- Semáforo de evidencia (extra; Gaby lo conecta en app.py bajo EXTRAS["semaforo"]) ---

# Cada color tiene un solo significado:
# - verde, amarillo y naranja: solo en la barra de solidez (qué tan segura es la comparación);
# - rojo: solo en la alerta de "rotan más";
# - "rotan menos" va en el color de texto normal: es un dato, no un juicio.
# No se usa el ÁMBAR de ui/tema.py, que ya significa "supuesto".
COLORES_SEMAFORO = {
    "naranja": "#F0883E",
    "amarillo": "#E5C547",
    "verde": "#3FB950",
}
ROJO_ALERTA = "#F85149"
APAGADO = "#2A3038"  # los segmentos de la barra que no están encendidos
_ROTULO = "font-size:13px;letter-spacing:2px;text-transform:uppercase;opacity:0.6;"


def _sin_dolar(texto):
    """"$2.3 M ... $6.3 M": Streamlit leería lo de en medio como fórmula; &#36; es el $ en HTML."""
    return texto.replace("$", "&#36;")


def html_direccion(dir_):
    """Pieza 1, el aviso de rotación: "↓ Rotan menos" en texto normal, o "⚠ Rotan más" en un recuadro rojo."""
    if dir_["rotan_mas"]:
        cuerpo = (
            f'<div style="border:2px solid {ROJO_ALERTA};border-radius:10px;padding:6px 12px;'
            'background:rgba(248,81,73,0.12);">'
            f'<div style="font-size:22px;font-weight:700;color:{ROJO_ALERTA};">{dir_["titulo"]}</div>'
            f'<div style="font-size:16px;opacity:0.85;">{dir_["detalle"]}</div></div>'
        )
    else:
        cuerpo = (
            f'<div style="font-size:22px;font-weight:700;">{dir_["titulo"]}</div>'
            f'<div style="font-size:16px;opacity:0.85;">{dir_["detalle"]}</div>'
        )
    return f'<div class="semaforo-direccion" style="margin:8px 0;"><div style="{_ROTULO}">Dirección</div>{cuerpo}</div>'


def html_solidez(sol):
    """Pieza 2, la barra de solidez: 3 segmentos, el activo encendido y la etiqueta siempre escrita."""
    color = COLORES_SEMAFORO[sol["color"]]
    segmentos = "".join(
        f'<div style="flex:1;height:14px;border-radius:7px;'
        f'background:{COLORES_SEMAFORO[c] if c == sol["color"] else APAGADO};"></div>'
        for c in sorted(NIVELES, key=NIVELES.get)
    )
    return (
        '<div class="semaforo-solidez" style="margin:8px 0;">'
        f'<div style="{_ROTULO}">Solidez</div>'
        f'<div style="display:flex;gap:6px;margin-top:4px;">{segmentos}</div>'
        f'<div style="font-size:20px;font-weight:600;color:{color};margin-top:6px;">● {sol["etiqueta"]}</div>'
        "</div>"
    )


def html_pesos(pesos):
    """Pieza 3, la frase de los pesos lado a lado. El $ va como &#36; para que no sea fórmula."""
    return f'<div class="semaforo-pesos" style="font-size:16px;opacity:0.85;margin:8px 0;">{_sin_dolar(pesos)}</div>'


def html_semaforo(dir_, sol, pesos=None):
    """Las tres piezas juntas, en orden: dirección, solidez y pesos.

    Funciones puras (no usan Streamlit), para poder probarlas. Las etiquetas siempre van
    escritas: el color solo no basta (daltonismo, proyector que lava el amarillo contra el naranja).
    """
    return html_direccion(dir_) + html_solidez(sol) + (html_pesos(pesos) if pesos else "")


# Cada pieza se puede dibujar sola, en el contenedor que Gaby elija. Las tres reciben el estado
# completo y no dibujan nada en el estado inicial (no hay comparación).

def dibujar_direccion(contenedor, estado):
    """Dibuja solo el aviso de rotación (↓ Rotan menos / ⚠ Rotan más)."""
    dir_ = direccion(estado)
    if dir_ is not None:
        with contenedor:
            st.markdown(html_direccion(dir_), unsafe_allow_html=True)


def dibujar_solidez(contenedor, estado):
    """Dibuja solo la barra de solidez (verde, amarillo o naranja)."""
    sol = solidez(estado)
    if sol is not None:
        with contenedor:
            st.markdown(html_solidez(sol), unsafe_allow_html=True)


def dibujar_pesos(contenedor, estado):
    """Dibuja solo la frase de los pesos (la medida contra la diferencia en bajas)."""
    pesos = lectura_pesos(estado)
    if pesos is not None:
        with contenedor:
            st.markdown(html_pesos(pesos), unsafe_allow_html=True)


def semaforo(contenedor, estado):
    """Atajo: las tres piezas juntas en el mismo contenedor, en orden.

    Se calcula solo con el estado, sin IA ni internet: cambia al instante con cada movimiento,
    igual que las cifras, sin esperar a que se pulse Explicar.
    """
    if direccion(estado) is None or solidez(estado) is None:
        return
    dibujar_direccion(contenedor, estado)
    dibujar_solidez(contenedor, estado)
    dibujar_pesos(contenedor, estado)


# --- Resumen descargable (crítica 4 del jurado) ---

ETIQUETA_RESUMEN = "Descargar resumen (PDF)"
AYUDA_RESUMEN = (
    "Baja un PDF para el comité con los escenarios guardados de esta empresa: cifras, solidez, "
    "costos y explicación. Si no ha guardado ninguno, lleva el que está en pantalla."
)


def _texto_vigente(estado, explicado):
    """La explicación de lo que está en pantalla, o None si falta pulsar Explicar."""
    if falta_explicar(estado, explicado):
        return None
    return ((explicado or {}).get("explicacion") or {}).get("texto")


def _pdf_seguro(estado, guardados, texto, fecha):
    """Arma el PDF. Si algo falla, devuelve un PDF con un aviso en vez de un archivo roto: nunca se cae la app."""
    from ia.resumen import armar_pdf, pdf_de_aviso

    try:
        return armar_pdf(estado, guardados, texto, fecha)[0]
    except Exception:  # noqa: BLE001  la descarga no puede tumbar la demo
        return pdf_de_aviso()


def pdf_en_memoria(memoria, escenarios, estado, guardados, texto, fecha):
    """El PDF ya armado, que se rehace solo cuando cambian los escenarios, la explicación o el día.

    El PDF se arma ANTES de dibujar el botón (no al pulsarlo): así la descarga no depende de que
    Streamlit conserve una función pendiente entre recargas, que fue lo que falló en el sandbox
    ("Deferred file ... not found"). Guardarlo en `memoria` evita rearmarlo con cada movimiento.
    """
    huella = json.dumps([escenarios, texto, f"{fecha:%Y-%m-%d}"], sort_keys=True, default=str, ensure_ascii=False)
    clave = hashlib.sha1(huella.encode("utf-8")).hexdigest()
    if memoria.get("clave") != clave:
        memoria["clave"], memoria["pdf"] = clave, _pdf_seguro(estado, guardados, texto, fecha)
    return memoria["pdf"]


def boton_resumen(contenedor, estado, guardados, explicado=None):
    """Dibuja «Descargar resumen (PDF)» con cuántos escenarios lleva. Devuelve True si se dibujó.

    - guardados: la lista de st.session_state["escenarios_guardados"] (la llena «Guardar escenario»).
    - explicado: el último estado explicado; su texto entra solo si sigue al día.
    Si la librería del PDF (fpdf2) no está instalada, no dibuja nada y la app sigue igual.
    """
    try:
        import fpdf  # noqa: F401  solo para saber si está instalada

        from ia.resumen import escenarios_para_resumen, nombre_archivo
    except ImportError:
        return False
    from datetime import datetime

    fecha = datetime.now().astimezone()
    texto = _texto_vigente(estado, explicado)
    guardados = list(guardados or [])
    escenarios = escenarios_para_resumen(estado, guardados, texto)
    total = len(escenarios)
    empresa = (estado.get("empresa") or {}).get("id")
    de_esta = sum(1 for g in guardados if ((g.get("estado") or {}).get("empresa") or {}).get("id") == empresa)
    etiqueta = f"{ETIQUETA_RESUMEN} · {total} escenario{'' if total == 1 else 's'}"
    if total < de_esta:  # guardó el mismo escenario más de una vez: que no parezca que se perdió alguno
        etiqueta += " sin repetir"
    memoria = st.session_state.setdefault("_resumen_pdf", {})
    datos = pdf_en_memoria(memoria, escenarios, estado, guardados, texto, fecha)
    with contenedor:
        st.download_button(
            etiqueta,
            data=datos,
            file_name=nombre_archivo(estado, fecha),
            mime="application/pdf",
            key="btn_resumen",
            help=AYUDA_RESUMEN,
            on_click="ignore",
            width="stretch",
        )
    return True
