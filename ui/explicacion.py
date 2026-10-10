"""Panel derecho: explicación de la IA, señal y n. Dueño: Julian."""
import streamlit as st

from ia.explicar import explicar


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


def render(contenedor, estado, anterior):
    """Dibuja el panel derecho: la explicación palabra por palabra y, debajo, la señal y el n.

    Si la IA escribió algo que el validador rechazó, el texto ya se vio en pantalla
    mientras llegaba. Al terminar, el panel se redibuja con estado["explicacion"]["texto"],
    que en ese caso es la plantilla: el texto malo dura en pantalla solo un instante.
    """
    with contenedor:
        caja = st.empty()  # un solo lugar para el texto: así se puede reemplazar al terminar
        pulso = st.empty()  # marcador invisible: tocarlo deja que Streamlit note un clic nuevo
        with caja.container():
            st.write_stream(_sin_latex_stream(explicar(estado, anterior, latido=pulso.empty)))
        final = (estado.get("explicacion") or {}).get("texto")
        if final:
            caja.markdown(sin_latex(final))
        st.caption(pie(estado))
