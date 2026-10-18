"""Prueba aislada de Restablecer con el controles.py real. No modifica ningún archivo del equipo.

Uso:  streamlit run sandbox/b_restablecer.py
1) Pulsa [+] en el aguinaldo.  2) Pulsa Restablecer.  3) Mira las cajas de abajo.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ui import controles

"""Banco de pruebas para encontrar qué hace fallar a Restablecer y a [+] / [−] en la app.

Uso:  streamlit run sandbox/b_restablecer.py
Arriba hay interruptores que reproducen, uno por uno, lo que tiene la app y no tiene una prueba mínima.
Empieza con todos apagados: debe funcionar. Enciéndelos de uno en uno y, después de cada cambio,
pulsa [+] en el aguinaldo y luego Restablecer. El interruptor que haga fallar es el culpable.
No modifica ningún archivo del equipo.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ui.tema import aplicar_estilos

st.set_page_config(layout="wide")
controles.DEPURAR = True  # panel de ayuda solo en esta prueba

c1, c2, c3, c4, c5 = st.columns(5)
estilos = c1.checkbox("1. Con estilos (tema.py)")
fragmento = c2.checkbox("2. Dentro de st.fragment")
guardar = c3.checkbox("3. Con «Guardar» (con_guardar=True)")
selector = c4.checkbox("4. Con selector encima")
columnas = c5.checkbox("5. Dentro de la columna izquierda")
st.divider()

if estilos:
    aplicar_estilos()

perfil = {
    "id": "PRUEBA",
    "plantilla_op": 1000,
    "palancas": {
        "sal_dia_ini": 323.61, "aguinaldo_op": 15, "prima_vac_op": 0.25, "vales_op": 0.09, "rutas_x100": 2.85,
    },
    "indicadores": {"rot_anual": 0.5, "rot_temprana": 0.4, "ausentismo": 0.015},
}


def cuerpo():
    if selector:
        st.radio("Empresa a analizar", ["Empresas de demo", "Mi empresa"], horizontal=True, key="p_radio")
        st.selectbox("Empresa", ["COMPAÑIA 36", "COMPAÑIA 29"], key="p_sel")
    resultado = controles.render(perfil, con_guardar=guardar)
    st.write("palancas_movidas:", resultado[0])


def pantalla():
    if columnas:
        izq, _centro, _der = st.columns([1.15, 2.2, 1.65], gap="large")
        with izq:
            cuerpo()
    else:
        cuerpo()


if fragmento:
    st.fragment(pantalla)()
else:
    pantalla()

controles.DEPURAR = True  # activa el panel de ayuda solo en esta prueba

perfil = {
    "id": "PRUEBA",
    "plantilla_op": 1000,
    "palancas": {
        "sal_dia_ini": 323.61, "aguinaldo_op": 15, "prima_vac_op": 0.25, "vales_op": 0.09, "rutas_x100": 2.85,
    },
    "indicadores": {"rot_anual": 0.5, "rot_temprana": 0.4, "ausentismo": 0.015},
}

palancas_movidas, cambio = controles.render(perfil)

st.write("palancas_movidas:", palancas_movidas)
st.write("Estado de la sesión (los botones salen en True solo en la ejecución del clic):")
st.json({k: v for k, v in st.session_state.items() if not str(k).startswith("_eventos")}, expanded=False)