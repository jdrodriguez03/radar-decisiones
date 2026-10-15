import unicodedata

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ui import procedencia
from ui.controles import CONTROLES
from ui.tema import ACENTO, AMBAR, GRIS, LINEA, TEXTO

COL_ID = "empresa"
COL_Y = "rot_anual"

EPS = 1e-9

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


def cifras_pesos(datos, columnas=None):
    """Las dos cifras en pesos, pintadas según su procedencia (ui/procedencia.py).

    Los costos de la medida y de la brecha son aritmética sobre lo observado y el perfil: calculado (gris).
    El costo por baja es un valor editable por el directivo: supuesto (ámbar).
    """
    izq, der = columnas or st.columns(2)
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


def mostrar_figura(fig, nombre_archivo):
    """Muestra una figura con las herramientas de siempre (zoom, captura, pantalla completa)."""
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "toImageButtonOptions": {"format": "png", "filename": nombre_archivo, "scale": 2},
        },
    )


def _norm(texto):
    """Compara nombres sin importar mayúsculas, espacios ni acentos (COMPAÑÍA = Compania)."""
    descompuesto = unicodedata.normalize("NFD", str(texto).strip().upper())
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")


def preparar_dispersion(datos, empresas, palancas=None):
    """Separa las empresas en grupo, resto, otras y la empresa elegida (según los ids del estado).

    palancas: una clave, una lista de claves o None; son las columnas de palancas que se conservan.
    """
    lista = [palancas] if isinstance(palancas, str) else list(palancas or [])
    columnas = [COL_ID, COL_Y, *lista]
    faltan = [c for c in columnas if c not in empresas.columns]
    if faltan:
        raise KeyError(
            f"empresas.parquet no tiene las columnas {faltan}. "
            f"Columnas disponibles: {list(empresas.columns)}"
        )
    df = empresas[columnas].copy()
    df["_id"] = df[COL_ID].map(_norm)

    ids_grupo = {_norm(i) for i in (datos["grupo"].get("ids") or [])}
    ids_resto = {_norm(i) for i in ((datos.get("resto") or {}).get("ids") or [])}
    propia = df["_id"] == _norm(datos["empresa"]["id"])

    elegida = df[propia]
    if elegida.empty:  # si no está en el parquet, se ubica con los datos del estado
        fila = {COL_ID: [datos["empresa"]["id"]], COL_Y: [datos["empresa"]["indicadores"]["rot_anual"]]}
        fila.update({p: [datos["empresa"]["palancas"][p]] for p in lista})
        elegida = pd.DataFrame(fila)
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

    if valor_x is not None:  # la empresa puede no tener dato en esa palanca
        fig.add_vline(x=valor_x, line_dash="dot", line_color=TEXTO)

    # Medianas de rotación anual; si no hay resto (nada movido) solo se dibuja la del grupo
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
    mostrar_figura(fig, "rotacion_por_palanca")


def _base_layout(fig, altura):
    fig.update_layout(
        height=altura,
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": TEXTO, "family": "Nunito, sans-serif", "size": 13},
    )


def distribucion_rotacion(datos, empresas, altura=330):
    """B. Distribución de la rotación anual: grupo contra resto, con la empresa elegida."""
    grupos = preparar_dispersion(datos, empresas)
    e = grupos["elegida"]
    rot_empresa = e[COL_Y].iloc[0]
    nombre_e = str(e[COL_ID].iloc[0])

    fig = go.Figure()
    capas = [
        (f"Grupo<br>(n={len(grupos['grupo'])})", ACENTO, grupos["grupo"]),
        (f"Resto<br>(n={len(grupos['resto'])})", GRIS, grupos["resto"]),
    ]
    for nombre, color, df in capas:
        if df.empty:
            continue
        fig.add_trace(go.Box(
            y=df[COL_Y], name=nombre, boxpoints="all", jitter=0.5, pointpos=0,
            marker={"color": color, "size": 6}, line={"color": color}, fillcolor="rgba(0,0,0,0)",
            hovertext=df[COL_ID], hoverinfo="text+y",
        ))
        fig.add_annotation(
            x=nombre, y=df[COL_Y].median(), text=f"Mediana {df[COL_Y].median():.0%}",
            showarrow=False, xanchor="left", xshift=34, yshift=14, font={"color": color},
        )

    fig.add_trace(go.Scatter(
        x=[nombre_e], y=[rot_empresa], mode="markers", name=nombre_e,
        hovertext=[nombre_e], hovertemplate="<b>%{hovertext}</b><br>Rotación anual: %{y:.1%}<extra></extra>",
        marker={"size": 18, "symbol": "diamond", "color": TEXTO, "line": {"color": ACENTO, "width": 2}},
    ))
    fig.add_hline(y=rot_empresa, line_dash="dot", line_color=TEXTO)

    _base_layout(fig, altura)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(tickangle=0)
    fig.update_yaxes(title_text="Rotación anual", tickformat=".0%", gridcolor=LINEA, zeroline=False)
    mostrar_figura(fig, "distribucion_rotacion")


def palancas_grupo(datos, empresas, niveles, altura=330):
    """C. Qué hace distinto el grupo: mediana de cada palanca (grupo, resto) y dónde está la empresa.

    Cada palanca se pone en una escala común de percentil entre las 40 empresas: 0% = el valor más bajo,
    100% = el más alto, 50% = la del medio. Los percentiles no se estiran por valores atípicos.
    niveles: valor actual de cada palanca en el escenario.
    """
    claves = list(CONTROLES)
    grupos = preparar_dispersion(datos, empresas, claves)
    todas = empresas[claves]
    reales = datos["empresa"]["palancas"]
    con_dato = [c for c in claves if not (reales.get(c) is None or reales.get(c) != reales.get(c))]
    nombres = [CONTROLES[c]["nombre"] for c in claves]

    def pos(clave, valor):
        """Percentil del valor entre las 40 empresas; los empates cuentan por la mitad."""
        col = todas[clave].dropna()
        return float(((col < valor).sum() + 0.5 * (col == valor).sum()) / len(col))

    def puntos(nombre_serie, valores, color, simbolo="circle", tam=13, borde=None, cs=None):
        cs = claves if cs is None else cs
        xs = [pos(c, valores[c]) for c in cs]
        textos = [f"{nombre_serie} · {CONTROLES[c]['nombre']}: {CONTROLES[c]['fmt'](valores[c])}" for c in cs]
        marcador = {"size": tam, "symbol": simbolo, "color": color}
        if borde:
            marcador["line"] = {"color": borde, "width": 2}
        return xs, go.Scatter(
            x=xs, y=[CONTROLES[c]["nombre"] for c in cs], mode="markers", name=nombre_serie,
            hovertext=textos, hoverinfo="text",
            marker=marcador,
        )

    med_grupo = {c: grupos["grupo"][c].median() for c in claves}
    hay_resto = not grupos["resto"].empty
    med_resto = {c: grupos["resto"][c].median() for c in claves} if hay_resto else None

    fig = go.Figure()

    if hay_resto:
        lx, ly = [], []
        for c, n in zip(claves, nombres):
            lx += [pos(c, med_grupo[c]), pos(c, med_resto[c]), None]
            ly += [n, n, None]
        fig.add_trace(go.Scatter(x=lx, y=ly, mode="lines", line={"color": LINEA, "width": 3},
                                 hoverinfo="skip", showlegend=False))

    series = [puntos("Grupo (mediana)", med_grupo, ACENTO)]
    if hay_resto:
        series.append(puntos("Resto (mediana)", med_resto, GRIS))
    series.append(puntos("Empresa hoy", reales, TEXTO, "diamond", 17, ACENTO, con_dato))
    movidas = {c: v for c, v in niveles.items() if c in con_dato and abs(v - reales[c]) > EPS}
    fuera = [c for c in movidas if movidas[c] < todas[c].min() - EPS or movidas[c] > todas[c].max() + EPS]
    if movidas:  # el escenario es un valor editable: color de supuesto
        xs = [pos(c, movidas[c]) for c in movidas]
        textos = [
            f"Empresa con el escenario · {CONTROLES[c]['nombre']}: {CONTROLES[c]['fmt'](v)}"
            + (" (fuera del rango observado)" if c in fuera else "")
            for c, v in movidas.items()
        ]
        fig.add_trace(go.Scatter(
            x=xs, y=[CONTROLES[c]["nombre"] for c in movidas], mode="markers",
            name="Empresa con el escenario", hovertext=textos, hoverinfo="text",
            marker={"size": 17, "symbol": "diamond-open", "color": AMBAR, "line": {"color": AMBAR, "width": 3}},
        ))
    for _, traza in series:
        fig.add_trace(traza)

    _base_layout(fig, altura)
    fig.update_layout(legend={"orientation": "h", "y": -0.25})
    fig.update_xaxes(
        title_text="Percentil entre las 40 empresas", tickformat=".0%",
        gridcolor=LINEA, zeroline=False, range=[-0.05, 1.05],
    )
    fig.update_yaxes(autorange="reversed", gridcolor=LINEA)
    mostrar_figura(fig, "palancas_grupo")
    st.caption("0% = valor más bajo entre las 40 empresas · 100% = valor más alto")
    for c in fuera:
        cfg = CONTROLES[c]
        st.markdown(
            procedencia.supuesto(
                f"⚠ {cfg['nombre']}: {cfg['fmt'](movidas[c])} está fuera del rango observado en las 40 empresas "
                f"({cfg['fmt'](todas[c].min())} a {cfg['fmt'](todas[c].max())}); se muestra en el extremo."
            ),
            unsafe_allow_html=True,
        )


def en_comun(datos):
    """Lo que el grupo tiene en común, tal como lo calculó el motor (dato observado)."""
    for item in datos.get("en_comun") or []:
        st.markdown(
            procedencia.observado(f'{item["texto"]}: grupo {item["grupo"]} · resto {item["resto"]}'),
            unsafe_allow_html=True,
        )