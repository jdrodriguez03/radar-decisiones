"""Radar de Decisiones. Única pieza que une todo. Dueño: Gaby."""
import json
from pathlib import Path

import streamlit as st

from ui.tema import aplicar_estilos

st.set_page_config(layout="wide")
aplicar_estilos()

ruta = Path(__file__).parent / "contrato" / "ejemplo.json"
datos = json.loads(ruta.read_text(encoding="utf-8"))

NOMBRES_PALANCAS = {
    "sal_dia_ini": "Salario diario inicial",
    "aguinaldo_op": "Aguinaldo (días)",
    "prima_vac_op": "Prima Vacacional",
    "vales_op": "Vales",
    "rutas_x100": "Rutas por 100",
}

NOMBRES_INDICADORES = {
    "rot_anual": "Rotación Anual",
    "rot_temprana": "Rotación Temprana",
    "ausentismo": "Ausentismo",
}


def html(texto):
    st.markdown(texto, unsafe_allow_html=True)


def pesos(valor):
    """$2,326,756 -> $2.326.756 (formato de la plantilla)."""
    return f"${valor:,.0f}".replace(",", ".")


def cifra_pesos(valor, etiqueta):
    return (
        f'<div class="peso">{pesos(valor)}</div>'
        f'<div class="peso-etiqueta">{etiqueta}</div>'
    )


empresa = datos["empresa"]
html('<div class="titulo-app">Radar de Decisiones</div>')
html(f'<div class="subtitulo">{empresa["id"]} - Plantilla {empresa["plantilla_op"]:,}</div>')

col_izq, col_centro, col_der = st.columns([1, 2, 1.3], gap="large")

# Columna izquierda: palancas
with col_izq:
    html('<div class="titulo-col">Palancas</div>')
    for clave, nombre in NOMBRES_PALANCAS.items():
        st.text_input(nombre, value=str(empresa["palancas"][clave]),
                      disabled=True, key=f"palanca_{clave}")
    b1, b2 = st.columns(2)
    b1.button("↻ Restablecer")
    b2.button("Guardar")

# Columna central: indicadores, gráfica, cifras en pesos
with col_centro:
    html('<div class="titulo-col">Indicadores</div>')

    filas = ""
    for clave, nombre in NOMBRES_INDICADORES.items():
        emp = empresa["indicadores"][clave]
        gru = datos["grupo"]["indicadores"][clave]
        res = datos["resto"]["indicadores"][clave]
        clase_grupo = "cifra-acento" if gru < res else "cifra"
        filas += (
            f'<tr><td class="nombre">{nombre}</td>'
            f'<td><span class="cifra">{emp:.1%}</span></td>'
            f'<td><span class="{clase_grupo}">{gru:.1%}</span></td>'
            f'<td><span class="cifra">{res:.1%}</span></td></tr>'
        )
    html(
        '<table class="tabla"><tr><th></th><th>Empresa</th><th>Grupo</th><th>Resto</th></tr>'
        f"{filas}</table>"
    )

    html('<div style="height:24px"></div>')
    p = datos["pesos"]
    p1, p2 = st.columns(2)
    with p1:
        html(cifra_pesos(p["costo_medida_anual"], "Costo Anual de la<br>Medida"))
    with p2:
        html(cifra_pesos(p["costo_brecha_anual"], "Costo Anual de la<br>Brecha"))

# Columna derecha: explicación, gráfica, señal y n
with col_der:
    html('<div class="titulo-col">Explicación</div>')
    html(f'<div class="explicacion">{datos["explicacion"]["texto"]}</div>')
    html('<div style="height:28px"></div>')
    html('<div class="grafica"><span class="texto-gris">Espacio para la gráfica</span></div>')
    senal = datos["senal"]
    html(f'<div class="texto-gris" style="margin-top:14px">Señal: {senal["etiqueta"]} (p = {senal["p"]})</div>')
    html(
        f'<div class="texto-gris">n grupo = {datos["grupo"]["n"]} · '
        f'n resto = {datos["resto"]["n"]}</div>'
    )
