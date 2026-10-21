import unicodedata

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ui import escenarios, procedencia
from ui.controles import CONTROLES
from ui.tema import ACENTO, AMBAR, GRIS, LINEA, TEXTO

COL_ID = "empresa"
COL_Y = "rot_anual"

EPS = 1e-9

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
    Un costo negativo es un ahorro: en lugar de «$-1.234.567» se muestra el título «Ahorro» y la cifra sin signo.
    """
    izq, der = columnas or st.columns(2)
    claves = ("costo_medida_anual", "costo_brecha_anual")
    hay_ahorro = any(datos["pesos"][c] < 0 for c in claves)
    for col, clave in zip((izq, der), claves):
        valor = datos["pesos"][clave]
        if valor < 0:
            titulo = '<div class="peso-ahorro">Ahorro</div>'
        elif hay_ahorro:
            titulo = '<div class="peso-ahorro" style="visibility:hidden">Ahorro</div>'
        else:
            titulo = ""
        col.markdown(
            f'{titulo}<div class="peso">{procedencia.calculado(pesos(abs(valor)))}</div>'
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
    hay_mejor = False
    for clave, nombre in NOMBRES_INDICADORES.items():
        emp = datos["empresa"]["indicadores"][clave]
        gru = (grupo.get("indicadores") or {}).get(clave)
        res = ind_resto.get(clave)

        mejor = gru is not None and emp is not None and gru < emp  
        hay_mejor = hay_mejor or mejor
        clase_grupo = "cifra-grande-acento" if mejor else "cifra-grande"
        marca = " ▼" if mejor else ""  # el color no es la única pista
        filas += (
            f'<tr><td class="nombre">{nombre}</td>'
            f'<td><span class="cifra-grande">{_fmt(emp)}</span></td>'
            f'<td><span class="{clase_grupo}">{_fmt(gru)}{marca}</span></td>'
            f'<td><span class="cifra-grande">{_fmt(res)}</span></td></tr>'
        )
    _html(
        '<table class="tabla"><tr><th></th><th>Situación actual</th><th>Empresas con las medidas</th>'
        "<th>Empresas sin las medidas</th></tr>"
        f"{filas}</table>"
    )
    if hay_mejor:
        _html('<div class="texto-gris">▼ las empresas con las medidas pierden menos que su empresa</div>')


def mostrar_figura(fig, nombre_archivo):
    """Muestra una figura con las herramientas de siempre (zoom, captura, pantalla completa)."""
    st.plotly_chart(
        fig,
        width="stretch",
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
    if elegida.empty:
        fila = {COL_ID: [datos["empresa"]["id"]], COL_Y: [datos["empresa"]["indicadores"]["rot_anual"]]}
        fila.update({p: [datos["empresa"]["palancas"][p]] for p in lista})
        elegida = pd.DataFrame(fila)
    return {
        "grupo": df[df["_id"].isin(ids_grupo) & ~propia],
        "resto": df[df["_id"].isin(ids_resto) & ~propia],
        "otras": df[~df["_id"].isin(ids_grupo | ids_resto) & ~propia],
        "elegida": elegida,
    }


def _base_layout(fig, altura):
    fig.update_layout(
        height=altura,
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": TEXTO, "family": "Nunito, sans-serif", "size": 16},
    )


X_BORDE = 1.14


def _apilar(valores, ancho=0.03, paso=0.17):
    """Desplazamiento vertical para que los puntos cercanos no se encimen."""
    colocados = []
    resultado = [0.0] * len(valores)
    for i in sorted(range(len(valores)), key=lambda j: valores[j]):
        for nivel in (0, 1, -1, 2, -2, 3, -3):
            if all(not (n == nivel and abs(valores[i] - px) < ancho) for px, n in colocados):
                colocados.append((valores[i], nivel))
                resultado[i] = nivel * paso
                break
    return resultado


def distribucion_rotacion(datos, empresas, altura=None):
    """Rotación anual por grupo: un punto por empresa, la mediana de cada grupo y la empresa hoy.

    El eje va de 0% a 100%; lo que pierde más de 100% se dibuja como triángulo en el carril "+100%".
    """
    grupos = preparar_dispersion(datos, empresas)
    e = grupos["elegida"]
    rot_e = float(e[COL_Y].iloc[0])
    nombre_e = str(e[COL_ID].iloc[0])
    filas = [(f"Con la medida ({len(grupos['grupo'])})", ACENTO, grupos["grupo"])]
    if not grupos["resto"].empty:
        filas.append((f"Sin la medida ({len(grupos['resto'])})", GRIS, grupos["resto"]))
    n = len(filas)

    def en_eje(v):
        return X_BORDE if v > 1 else v

    fig = go.Figure()
    hay_fuera = rot_e > 1
    for i, (_, color, df) in enumerate(filas):
        y0 = n - 1 - i
        valores = [float(v) for v in df[COL_Y]]
        nombres = [str(x) for x in df[COL_ID]]
        desp = _apilar([en_eje(v) for v in valores])
        for fuera, simbolo in ((False, "circle"), (True, "triangle-right")):
            idx = [k for k, v in enumerate(valores) if (v > 1) == fuera]
            if not idx:
                continue
            hay_fuera = hay_fuera or fuera
            fig.add_trace(go.Scatter(
                x=[en_eje(valores[k]) for k in idx], y=[y0 + desp[k] for k in idx], mode="markers",
                hovertext=[f"{nombres[k]}: {valores[k]:.0%}" for k in idx], hoverinfo="text",
                marker={"size": 13 if not fuera else 15, "symbol": simbolo, "color": color},
            ))
        med = float(df[COL_Y].median())
        fig.add_shape(type="line", x0=en_eje(med), x1=en_eje(med), y0=y0 - 0.36, y1=y0 + 0.36,
                      line={"color": color, "width": 5})
        fig.add_annotation(x=en_eje(med), y=y0 + 0.36, text=f"{med:.0%}", showarrow=False,
                           yshift=14, font={"color": TEXTO, "size": 18})


    xe = en_eje(rot_e)
    y_top = n - 0.1
    fig.add_shape(type="line", x0=xe, x1=xe, y0=-0.6, y1=y_top, line={"color": TEXTO, "width": 2, "dash": "dash"})
    fig.add_trace(go.Scatter(
        x=[xe], y=[y_top], mode="markers", hovertext=[f"{nombre_e}: {rot_e:.0%}"], hoverinfo="text",
        marker={"size": 18, "symbol": "diamond", "color": TEXTO},
    ))
    derecha = xe > 0.45
    fig.add_annotation(x=xe, y=y_top, text=f"Empresa hoy: {rot_e:.0%}", showarrow=False,
                       xanchor="right" if derecha else "left", xshift=-16 if derecha else 16,
                       font={"color": TEXTO, "size": 18})

    valores_eje, textos_eje = [0, 0.25, 0.5, 0.75, 1.0], ["0%", "25%", "50%", "75%", "100%"]
    if hay_fuera:
        valores_eje.append(X_BORDE)
        textos_eje.append("+100%")
        fig.add_shape(type="line", x0=X_BORDE - 0.07, x1=X_BORDE - 0.07, y0=-0.6, y1=n - 0.3,
                      line={"color": LINEA, "width": 1, "dash": "dot"})

    _base_layout(fig, altura or 150 + 110 * n)
    fig.update_layout(showlegend=False, margin={"l": 10, "r": 10, "t": 10, "b": 10})
    fig.update_xaxes(range=[-0.03, X_BORDE + 0.07 if hay_fuera else 1.03], tickvals=valores_eje,
                     ticktext=textos_eje, gridcolor=LINEA, zeroline=False, tickfont={"size": 15}, tickangle=0,
                     title_text="Rotación Anual", title_font={"size": 16, "color": TEXTO}, automargin=True)
    fig.update_yaxes(range=[-0.7, n + 0.25], tickvals=[n - 1 - i for i in range(n)],
                     ticktext=[f[0] for f in filas], showgrid=False, zeroline=False,
                     fixedrange=True, tickfont={"size": 18})
    mostrar_figura(fig, "rotacion_por_grupo")


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

    series = [puntos("Con la medida (mediana)", med_grupo, ACENTO)]
    if hay_resto:
        series.append(puntos("Sin la medida (mediana)", med_resto, GRIS, "square"))
    series.append(puntos("Empresa hoy", reales, TEXTO, "diamond", 17, ACENTO, con_dato))
    movidas = {c: v for c, v in niveles.items() if c in con_dato and abs(v - reales[c]) > EPS}
    # Escenarios fuera de lo observado: el percentil se queda en 0% o 100%, así que se avisa
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


def _palancas_escenario(escenario):
    """«Aguinaldo (días) 20 · Prima Vacacional 50.0%», o «sin cambios» si no se movió nada."""
    movidas = escenario.get("palancas_movidas") or {}
    if not movidas:
        return "sin cambios"
    return " · ".join(f'{CONTROLES[c]["nombre"]} {CONTROLES[c]["fmt"](v)}' for c, v in movidas.items() if c in CONTROLES)


def _entero(v):
    return f"{v:g}"


def _pct(v):
    return f"{v:.1%}"


def _puntos(v):
    """Diferencia entre dos porcentajes, en puntos porcentuales: 0.052 -> «5.2 pp»."""
    return f"{v * 100:.1f} pp"


def _con_signo(valor, formato):
    if valor is None:
        return "—"
    signo = "+" if valor > 0 else ("−" if valor < 0 else "")
    return signo + formato(abs(valor))


def escenarios_ab(guardados, al_limpiar):
    """Extra: los escenarios A y B lado a lado, con la diferencia B − A (la calcula ui/escenarios.py)."""
    if not guardados:
        return
    a = guardados[0]
    if len(guardados) == 1:
        _html(
            f'<div class="texto-gris" style="margin-top:12px">Escenario A guardado ({a["empresa"]["id"]}: '
            f"{_palancas_escenario(a)}). Mueva las palancas y pulse «Guardar escenario» para el B.</div>"
        )
        st.button("Limpiar A y B", key="btn_limpiar_ab", on_click=al_limpiar)
        return

    b = guardados[1]
    dif = escenarios.comparar_escenarios(a["estado"], b["estado"])
    filas = [
        ("Empresas en el grupo", dif["n_grupo"], _entero, _entero),
        ("Rotación anual del grupo", dif["rotacion_grupo"], _pct, _puntos),
        ("Costo anual de la medida", dif["costo_medida"], pesos, pesos),
        ("Costo anual de la brecha", dif["costo_brecha"], pesos, pesos),
    ]
    html = ""
    for nombre, d, fmt, fmt_dif in filas:
        html += (
            f'<tr><td class="nombre">{nombre}</td>'
            f'<td><span class="cifra">{"—" if d["a"] is None else fmt(d["a"])}</span></td>'
            f'<td><span class="cifra">{"—" if d["b"] is None else fmt(d["b"])}</span></td>'
            f'<td><span class="cifra">{_con_signo(d["diferencia_b_menos_a"], fmt_dif)}</span></td></tr>'
        )
    senal = dif["senal"]
    html += (
        '<tr><td class="nombre">Señal</td>'
        f'<td>{senal["a"].get("etiqueta", "—")}</td><td>{senal["b"].get("etiqueta", "—")}</td>'
        f'<td>{"cambia" if senal["cambio"] else "igual"}</td></tr>'
    )
    _html(
        '<div class="grafica-titulo" style="margin-top:18px">Escenarios A y B</div>'
        '<table class="tabla tabla-ab"><tr><th></th><th>A</th><th>B</th><th>B − A</th></tr>'
        f"{html}</table>"
        f'<div class="texto-gris" style="margin-top:6px">A · {a["empresa"]["id"]}: {_palancas_escenario(a)}<br>'
        f'B · {b["empresa"]["id"]}: {_palancas_escenario(b)}</div>'
    )
    st.button("Limpiar A y B", key="btn_limpiar_ab", on_click=al_limpiar)
