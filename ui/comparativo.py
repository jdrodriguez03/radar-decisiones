import unicodedata

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ui import procedencia
from ui.controles import CONTROLES
from ui.tema import ACENTO, GRIS, LINEA, TEXTO

COL_ID = "empresa"
COL_Y = "rot_anual"

FORMATO_X = {
    "sal_dia_ini": "$,.0f",
    "aguinaldo_op": ".0f",
    "prima_vac_op": ".0%",
    "vales_op": ".1%",
    "rutas_x100": ".1f",
}

NOMBRES_INDICADORES = {
    "rot_anual": "Rotación Anual",
    "rot_temprana": "Rotación Temprana",
    "ausentismo": "Ausentismo",
}


def _html(texto):
    st.markdown(texto, unsafe_allow_html=True)


@st.cache_data
def cargar_empresas(ruta):
    """Lee empresas.parquet una sola vez; después sale de la caché."""
    return pd.read_parquet(ruta)


def pesos(valor):
    """2326756 -> $2.326.756 (formato de la plantilla)."""
    return f"${valor:,.0f}".replace(",", ".")


ETIQUETAS_PESOS = {
    "costo_medida_anual": "Costo Anual de la Medida",
    "costo_brecha_anual": "Costo Anual de la Brecha",
}


def cifras_pesos(datos):
    """Las dos cifras en pesos, pintadas según su procedencia (ui/procedencia.py).

    Los costos de la medida y de la brecha son aritmética sobre lo observado y el perfil: calculado (gris).
    El costo por baja es un valor editable por el directivo: supuesto (ámbar).
    """
    izq, der = st.columns(2)
    for col, clave in zip((izq, der), ("costo_medida_anual", "costo_brecha_anual")):
        col.markdown(
            f'<div class="peso">{procedencia.calculado(pesos(datos["pesos"][clave]))}</div>'
            f'<div class="peso-etiqueta">{ETIQUETAS_PESOS[clave]}</div>',
            unsafe_allow_html=True,
        )
    costo_baja = (datos["pesos"].get("supuestos") or {}).get("costo_por_baja")
    if costo_baja is not None:
        st.markdown(
            '<div class="peso-etiqueta" style="margin-top:10px">'
            f'{procedencia.supuesto("Supuesto: costo por baja " + pesos(costo_baja))}</div>',
            unsafe_allow_html=True,
        )


def _fmt(valor):
    """Porcentaje con un decimal; guion si el dato no existe (por ejemplo, resto sin grupo)."""
    return "—" if valor is None else f"{valor:.1%}"


def render(datos):
    """Comparativo: empresa, grupo y resto en grande, con encabezado y aviso de grupo completado."""
    grupo = datos["grupo"]
    ind_resto = (datos.get("resto") or {}).get("indicadores") or {}

    _html(f'<div class="comp-encabezado">Comparando con {grupo["n"]} empresas reales</div>')

    if grupo.get("completado"):
        _html('<div class="comp-aviso">Grupo completado con empresas similares</div>')

    filas = ""
    for clave, nombre in NOMBRES_INDICADORES.items():
        emp = datos["empresa"]["indicadores"][clave]
        gru = (grupo.get("indicadores") or {}).get(clave)
        res = ind_resto.get(clave)
        clase_grupo = "cifra-grande-acento" if gru is not None and gru < emp else "cifra-grande"
        filas += (
            f'<tr><td class="nombre">{nombre}</td>'
            f'<td><span class="cifra-grande">{_fmt(emp)}</span></td>'
            f'<td><span class="{clase_grupo}">{_fmt(gru)}</span></td>'
            f'<td><span class="cifra-grande">{_fmt(res)}</span></td></tr>'
        )
    _html(
        '<table class="tabla"><tr><th></th><th>Empresa</th><th>Grupo</th><th>Resto</th></tr>'
        f"{filas}</table>"
    )


def _norm(texto):
    """Compara nombres sin importar mayúsculas, espacios ni acentos (COMPAÑÍA = Compania)."""
    descompuesto = unicodedata.normalize("NFD", str(texto).strip().upper())
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")


def preparar_dispersion(datos, empresas, palanca_x):
    """Separa las empresas en grupo, resto, otras y la empresa elegida (según los ids del estado)."""
    faltan = [c for c in (COL_ID, COL_Y, palanca_x) if c not in empresas.columns]
    if faltan:
        raise KeyError(
            f"empresas.parquet no tiene las columnas {faltan}. "
            f"Columnas disponibles: {list(empresas.columns)}"
        )
    df = empresas[[COL_ID, palanca_x, COL_Y]].copy()
    df["_id"] = df[COL_ID].map(_norm)

    ids_grupo = {_norm(i) for i in (datos["grupo"].get("ids") or [])}
    ids_resto = {_norm(i) for i in ((datos.get("resto") or {}).get("ids") or [])}
    propia = df["_id"] == _norm(datos["empresa"]["id"])

    elegida = df[propia]
    if elegida.empty:
        elegida = pd.DataFrame({
            COL_ID: [datos["empresa"]["id"]],
            palanca_x: [datos["empresa"]["palancas"][palanca_x]],
            COL_Y: [datos["empresa"]["indicadores"]["rot_anual"]],
        })
    return {
        "grupo": df[df["_id"].isin(ids_grupo) & ~propia],
        "resto": df[df["_id"].isin(ids_resto) & ~propia],
        "otras": df[~df["_id"].isin(ids_grupo | ids_resto) & ~propia],
        "elegida": elegida,
    }


def dispersion(datos, empresas, palanca_x, valor_x):
    """Dispersión: eje X = palanca elegida, eje Y = rotación anual.

    palanca_x: última palanca movida (o "sal_dia_ini" si no hay).
    valor_x: nivel actual de esa palanca (línea punteada vertical).
    Las líneas horizontales son la mediana de rotación anual del grupo y del resto.
    """
    grupos = preparar_dispersion(datos, empresas, palanca_x)
    formato = FORMATO_X.get(palanca_x, ".2f")
    hover = f"<b>%{{hovertext}}</b><br>X: %{{x:{formato}}}<br>Rotación anual: %{{y:.1%}}<extra></extra>"

    fig = go.Figure()
    capas = [
        ("Grupo", {"size": 10, "color": ACENTO}, grupos["grupo"]),
        ("Resto", {"size": 10, "color": GRIS}, grupos["resto"]),
        # círculo hueco para que se vea sobre el fondo oscuro
        ("Sin clasificar", {"size": 10, "color": "rgba(0,0,0,0)", "line": {"color": GRIS, "width": 1.5}},
         grupos["otras"]),
    ]
    for nombre, marcador, df in capas:
        if df.empty:
            continue
        fig.add_trace(go.Scatter(
            x=df[palanca_x], y=df[COL_Y], mode="markers", name=nombre,
            hovertext=df[COL_ID], hovertemplate=hover, marker=marcador,
        ))

    e = grupos["elegida"]
    fig.add_trace(go.Scatter(
        x=e[palanca_x], y=e[COL_Y], mode="markers", name=f"{e[COL_ID].iloc[0]} (elegida)",
        hovertext=e[COL_ID], hovertemplate=hover,
        marker={"size": 20, "symbol": "diamond", "color": TEXTO, "line": {"color": ACENTO, "width": 2}},
    ))

    fig.add_vline(x=valor_x, line_dash="dot", line_color=TEXTO)


    medianas = [
        ("grupo", ACENTO, grupos["grupo"][COL_Y].median(), "top right"),
        ("resto", GRIS, grupos["resto"][COL_Y].median(), "bottom right"),
    ]
    for nombre, color, valor, posicion in medianas:
        if pd.isna(valor):
            continue
        fig.add_hline(
            y=valor, line_dash="dash", line_color=color,
            annotation_text=f"Mediana {nombre}: {valor:.0%}",
            annotation_position=posicion, annotation_font_color=color,
        )

    fig.update_layout(
        height=380,
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": TEXTO, "family": "Nunito, sans-serif", "size": 14},
        legend={"orientation": "h", "y": -0.2},
        xaxis={"title": CONTROLES[palanca_x]["nombre"], "tickformat": formato,
               "gridcolor": LINEA, "zeroline": False},
        yaxis={"title": "Rotación anual", "tickformat": ".0%", "gridcolor": LINEA, "zeroline": False},
    )
    st.plotly_chart(fig, use_container_width=True)