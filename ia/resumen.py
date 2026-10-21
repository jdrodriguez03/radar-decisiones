"""Resumen en PDF para llevar al comité (crítica 4 del jurado). Dueño: Julian.

El directivo registra escenarios con «Guardar escenario» y pulsa «Descargar resumen»: baja un
informe tamaño carta con la situación actual de la compañía, una tabla con todos los escenarios y
el detalle de cada uno (cifras, solidez de la evidencia, interpretación y consideraciones).

Reglas:
- No calcula nada nuevo ni llama a la IA: solo ordena lo que ya está en los estados guardados.
  Funciona sin internet y se arma en el mismo computador donde corre la app.
- Ninguna cifra inventada: antes de dibujar, cada texto con cifras pasa por el mismo validador de la
  IA (ia/validador.py). Si un texto no pasa, se escribe "Dato no disponible" en su lugar.
- Lenguaje corporativo y sin promesas: describe lo que muestran las empresas que ya lo hacen.
- Tres pasos, para poder probarlo: contenido() arma los textos (función pura), asegurar_cifras()
  los valida y dibujar() los convierte en PDF con fpdf2.
- Todo el estilo (colores, letras, tamaños, textos fijos) está en el bloque «Estilo del informe»:
  un cambio de estilo se hace ahí, sin tocar lo demás.
"""
import re
import unicodedata
from datetime import datetime

from ia.prompts import aviso_senal, rasgos_utiles
from ia.semaforo import direccion, solidez
from ia.validador import cifras_inventadas

MESES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)

# Cómo se nombra cada palanca y cómo se escribe su valor.
ETIQUETAS = {
    "sal_dia_ini": "Salario inicial",
    "aguinaldo_op": "Aguinaldo",
    "prima_vac_op": "Prima vacacional",
    "vales_op": "Vales de despensa",
    "rutas_x100": "Rutas",
}
FORMATOS = {
    "sal_dia_ini": lambda v: f"${v:,.0f}",
    "aguinaldo_op": lambda v: f"{v:g} días",
    "prima_vac_op": lambda v: f"{v:.0%}",
    "vales_op": lambda v: f"{round(v * 100, 1):g}%",
    "rutas_x100": lambda v: f"{round(v, 2):g} por cada 100",
}

# ---------------------------------------------------------------------------
# Textos fijos del informe
# ---------------------------------------------------------------------------
SIN_DATO = "Dato no disponible"
SIN_CAMBIOS = "Situación actual (sin cambios)"
SIN_EXPLICACION = "Sin interpretación: el escenario se registró antes de pulsar «Explicar»."
SIN_COMPARACION = "Sin comparación"
SOLIDEZ_CORTA = {"verde": "Evidencia clara", "amarillo": "Evidencia débil", "naranja": "No concluyente"}

SUBTITULO = "Documento de apoyo para el comité de dirección"
INTRODUCCION = (
    "Este documento resume los escenarios de compensación evaluados para la compañía. Cada escenario se "
    "contrasta con las empresas de la encuesta que ya otorgan ese nivel de prestaciones y con las que no lo "
    "hacen. Las cifras describen lo observado en dichas empresas y no constituyen una proyección de "
    "resultados para la compañía."
)
NOTA_SUPUESTOS = "* Supuestos definidos por la dirección; pueden modificarse en la herramienta."
NOTA_TABLA = (
    "Con / sin la medida: número de empresas que ya aplican el escenario y de las que no. Rotación anual: "
    "mediana de cada conjunto. Costo de la medida y brecha (costo anual de la rotación adicional frente a las "
    "empresas con la medida), en pesos al año; «Ahorro» indica que la medida reduce costos y un «-» que la "
    "compañía ya rota menos que las empresas con la medida. (*) Completado con empresas de perfil similar. "
    "En rojo: las empresas con la medida presentan una rotación igual o superior a la de las empresas sin ella."
)
METODOLOGIA = (
    "El análisis se basa en la encuesta de rotación de 40 empresas, con datos anónimos. Para cada escenario "
    "se comparan las empresas con la medida, que ya otorgan al menos el nivel seleccionado en cada "
    "prestación, con las empresas sin la medida. Las rotaciones corresponden a medianas. La solidez de la evidencia se determina con "
    "la prueba de Mann-Whitney: clara (p < 0.05), débil (p < 0.15) o no concluyente. Cuando menos de cinco "
    "empresas cumplen el escenario, se completan con empresas de perfil similar y el resultado se "
    "reporta como no concluyente. Los costos dependen de los supuestos indicados, definidos por la dirección "
    "y modificables en la herramienta."
)
FUENTE = "Fuente: encuesta de rotación de 40 empresas, datos anónimos"
AVISO_ROTAN_MAS = (
    "Las empresas con la medida presentan una rotación igual o superior a la de las empresas sin ella; no se observa una "
    "ventaja asociada a esta medida."
)
AVISO_COMPLETADO = (
    "Pocas empresas cumplen esta combinación, por lo que se completaron con empresas de perfil "
    "similar. El resultado debe tomarse como referencia."
)
AVISO_NO_CONCLUYENTE = (
    "La diferencia observada no es estadísticamente concluyente. El resultado debe tomarse como referencia."
)
AVISO_FALLA = (
    "No se pudo generar el informe con estos escenarios. Pulse «Restablecer», registre de nuevo los "
    "escenarios y vuelva a descargar."
)


# ---------------------------------------------------------------------------
# 1. Qué escenarios entran
# ---------------------------------------------------------------------------
def _firma(estado):
    """Dos escenarios son el mismo si tienen las mismas palancas movidas y los mismos supuestos."""
    movidas = tuple(sorted((estado.get("palancas_movidas") or {}).items()))
    supuestos = tuple(sorted(((estado.get("pesos") or {}).get("supuestos") or {}).items()))
    grupo = estado.get("grupo") or {}
    return movidas, supuestos, grupo.get("n"), (estado.get("resto") or {}).get("n")


def escenarios_para_resumen(estado, guardados, texto_actual=None):
    """La lista de escenarios del informe, en el orden en que se guardaron.

    - Solo los de la empresa que está en pantalla: un informe es de una sola compañía.
    - Si un escenario se guardó dos veces igual, queda una vez, con su explicación más reciente.
    - Si no hay ninguno guardado de esta empresa, entra el que está en pantalla, con su explicación
      (texto_actual) solo si está al día.
    Cada escenario es {"estado", "explicacion" (texto o None), "hora" (ISO o None)}.
    """
    empresa = (estado.get("empresa") or {}).get("id")
    elegidos = {}
    for guardado in guardados or []:
        previo = guardado.get("estado") or {}
        if (previo.get("empresa") or {}).get("id") != empresa:
            continue
        firma = _firma(previo)
        nuevo = {"estado": previo, "explicacion": guardado.get("explicacion"), "hora": guardado.get("hora")}
        if firma in elegidos and not nuevo["explicacion"]:
            nuevo["explicacion"] = elegidos[firma]["explicacion"]  # no perder una explicación ya guardada
        elegidos[firma] = nuevo  # un dict conserva el orden de la primera vez que se guardó
    if elegidos:
        return list(elegidos.values())
    return [{"estado": estado, "explicacion": texto_actual, "hora": None}]


# ---------------------------------------------------------------------------
# 2. Textos (funciones puras: no dibujan nada y se pueden probar)
# ---------------------------------------------------------------------------
def _millones(pesos):
    """6341580 -> '$6.3 M'; menos de un millón va completo (85000 -> '$85,000'), para no escribir '$0.1 M'."""
    if abs(pesos) < 1_000_000:
        return f"${abs(pesos):,.0f}"
    return f"${abs(pesos) / 1_000_000:.1f} M"


def _pesos(pesos):
    """15000 -> '$15,000'"""
    return f"${pesos:,.0f}"


def fecha_larga(fecha):
    return f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"


def _hora(iso):
    """'2026-10-21T10:42:05-05:00' -> '10:42'; None si no se puede leer."""
    try:
        return datetime.fromisoformat(iso).strftime("%H:%M")
    except (TypeError, ValueError):
        return None


def texto_supuestos(supuestos):
    """{'costo_por_baja': 15000, 'costo_ruta_mensual': 35000} -> '$15,000 por baja · $35,000 al mes por ruta'"""
    partes = []
    if supuestos.get("costo_por_baja") is not None:
        partes.append(f"{_pesos(supuestos['costo_por_baja'])} por baja")
    if supuestos.get("costo_ruta_mensual") is not None:
        partes.append(f"{_pesos(supuestos['costo_ruta_mensual'])} al mes por ruta")
    return " · ".join(partes)


def combinacion_larga(estado):
    """'Aguinaldo de 15 días a 20 días; Prima vacacional de 25% a 50%'."""
    movidas = estado.get("palancas_movidas") or {}
    reales = (estado.get("empresa") or {}).get("palancas") or {}
    partes = []
    for palanca, valor in movidas.items():
        if palanca not in ETIQUETAS:
            continue
        nombre, formato = ETIQUETAS[palanca], FORMATOS[palanca]
        if reales.get(palanca) is None:
            partes.append(f"{nombre} a {formato(valor)}")
        else:
            partes.append(f"{nombre} de {formato(reales[palanca])} a {formato(valor)}")
    return "; ".join(partes) if partes else SIN_CAMBIOS


def _porcentaje(v):
    """0.1 -> '10%', 0.065 -> '6.5%'"""
    return f"{round(v * 100, 1):g}%"


# Cómo escribir las medianas de «qué tienen en común», según el rasgo (los textos vienen de
# motor/en_comun.py). Los motivos de baja y el fondo de ahorro son proporciones: van en %.
FORMATO_RASGO = (
    ("salario inicial", lambda v: f"${v:,.0f}"),
    ("aguinaldo", lambda v: f"{v:g} días"),
    ("vales", _porcentaje),
    ("rutas", lambda v: f"{round(v, 2):g}"),  # el texto ya dice "rutas por cada 100 operativos"
    ("fondo de ahorro", _porcentaje),
    ("motivo de baja", _porcentaje),
)


def _valor_rasgo(texto, valor):
    if isinstance(valor, (str, bool)) or valor is None:
        return str(valor)
    for inicio, formato in FORMATO_RASGO:
        if texto.startswith(inicio):
            return formato(valor)
    return f"{valor:g}"


def _rasgo(rasgo):
    """Una diferencia entre el grupo y el resto, con sus dos cifras tal como vienen del motor.

    motor/en_comun.py devuelve las DIFERENCIAS más grandes entre grupo y resto, que pueden ir en
    cualquier sentido ("0 de 5" frente a "13 de 33"): por eso se dice «diferencia», nunca «en común».
    'motivo de baja: estudios' -> 'motivo de baja por estudios (50% con la medida, frente a 10% sin ella)'
    """
    texto = rasgo.get("texto", "")
    grupo, resto = _valor_rasgo(texto, rasgo.get("grupo")), _valor_rasgo(texto, rasgo.get("resto"))
    nombre = texto.replace("motivo de baja: ", "motivo de baja por ", 1)
    return f"{nombre} ({grupo} con la medida, frente a {resto} sin ella)"


def _tipo(estado):
    """'actual' (sin palancas movidas), 'sin_comparacion' (todas o ninguna cumplen) o 'normal'."""
    if not estado.get("palancas_movidas"):
        return "actual"
    return "normal" if direccion(estado) is not None else "sin_comparacion"


def _rotaciones(estado):
    grupo, resto = estado["grupo"], estado["resto"]
    return grupo["indicadores"]["rot_anual"], resto["indicadores"]["rot_anual"]


def fila(numero, estado):
    """Un renglón de la tabla: 7 celdas y cómo pintarlas."""
    grupo, resto, pesos = estado.get("grupo") or {}, estado.get("resto") or {}, estado.get("pesos") or {}
    tipo = _tipo(estado)
    nombre = combinacion_larga(estado).replace("; ", ", ")
    if tipo == "actual":
        celdas = [str(numero), nombre, f"{grupo.get('n', 0)}", "-", "-", "-", "-"]
        return {"celdas": celdas, "color": None, "rotan_mas": False}
    if tipo == "sin_comparacion":
        celdas = [str(numero), nombre, f"{grupo.get('n', 0)} / {resto.get('n', 0)}", "-", SIN_COMPARACION, "-", "-"]
        return {"celdas": celdas, "color": None, "rotan_mas": False}
    dir_, sol = direccion(estado), solidez(estado)
    rot_g, rot_r = _rotaciones(estado)
    medida, brecha = pesos.get("costo_medida_anual"), pesos.get("costo_brecha_anual")
    texto_medida = "-" if medida is None else (f"Ahorro {_millones(medida)}" if medida < 0 else _millones(medida))
    texto_brecha = "-" if not brecha else _millones(brecha)
    celdas = [
        str(numero), nombre, f"{grupo['n']} / {resto['n']}" + (" *" if grupo.get("completado") else ""),
        f"{rot_g:.0%} vs {rot_r:.0%}", SOLIDEZ_CORTA[sol["color"]] if sol else "-", texto_medida, texto_brecha,
    ]
    return {"celdas": celdas, "color": sol["color"] if sol else None, "rotan_mas": dir_["rotan_mas"]}


MAX_EXPLICACION = 900  # caracteres; las explicaciones reales tienen menos de 500 (máximo 75 palabras)


def _recortar(texto):
    """Un texto anormalmente largo se corta en la última palabra completa, para que el bloque quepa en una hoja."""
    if not texto or len(texto) <= MAX_EXPLICACION:
        return texto
    return texto[:MAX_EXPLICACION].rsplit(" ", 1)[0] + "..."


def detalle(numero, escenario):
    """El bloque de un escenario: título, franja de cifras, solidez, supuestos, interpretación y consideraciones."""
    estado = escenario["estado"]
    grupo, resto, pesos = estado.get("grupo") or {}, estado.get("resto") or {}, estado.get("pesos") or {}
    tipo = _tipo(estado)
    explicacion = _recortar(escenario.get("explicacion"))
    consideraciones = []  # (tono, texto); tono "rojo" para la alerta de que el grupo rota más
    solidez_texto, color = None, None
    if tipo == "actual":
        rot = ((estado.get("empresa") or {}).get("indicadores") or {}).get("rot_anual")
        cifras = [
            ("Empresas comparadas", f"{grupo.get('n', 0)}"),
            ("Rotación de la compañía", f"{rot:.0%}" if rot is not None else "-"),
            ("Costo anual de la medida", "-"),
            ("Costo anual de la brecha", "-"),
        ]
        interpretacion = "Situación actual de la compañía, sin cambios en las prestaciones."
    elif tipo == "sin_comparacion":
        cifras = [
            ("Empresas: con / sin la medida", f"{grupo.get('n', 0)} / {resto.get('n', 0)}"),
            ("Rotación: con / sin la medida", "-"),
            ("Costo anual de la medida", "-"),
            ("Costo anual de la brecha", "-"),
        ]
        consideraciones.append(("", (
            f"No es posible comparar: {grupo.get('n', 0)} empresas con dato cumplen esta combinación y "
            f"{resto.get('n', 0)} no la cumplen. Se sugiere evaluar un nivel superior al actual de la compañía."
        )))
        interpretacion = explicacion or SIN_EXPLICACION
    else:
        dir_, sol = direccion(estado), solidez(estado)
        rot_g, rot_r = _rotaciones(estado)
        medida, brecha = pesos.get("costo_medida_anual"), pesos.get("costo_brecha_anual")
        cifras = [
            ("Empresas: con / sin la medida", f"{grupo['n']} / {resto['n']}"),
            ("Rotación: con / sin la medida", f"{rot_g:.0%} / {rot_r:.0%}"),
            ("Costo anual de la medida",
             "-" if medida is None else (f"Ahorro de {_millones(medida)}" if medida < 0 else _millones(medida))),
            ("Costo anual de la brecha", "Sin brecha" if not brecha else _millones(brecha)),
        ]
        if sol:
            solidez_texto, color = sol["etiqueta"], sol["color"]
        ya_lo_dice = (explicacion or "").lower()  # no repetir lo que la interpretación ya advierte
        if dir_["rotan_mas"]:
            consideraciones.append(("rojo", AVISO_ROTAN_MAS))
        if grupo.get("completado") and "complet" not in ya_lo_dice:
            consideraciones.append(("", AVISO_COMPLETADO))
        elif aviso_senal(estado) and not grupo.get("completado") and "concluyente" not in ya_lo_dice:
            consideraciones.append(("", AVISO_NO_CONCLUYENTE))
        interpretacion = explicacion or SIN_EXPLICACION
    for rasgo in rasgos_utiles(estado)[:2] if tipo != "actual" else []:
        consideraciones.append(("", f"Diferencia con las empresas sin la medida: {_rasgo(rasgo)}."))
    return {
        "numero": numero,
        "titulo": combinacion_larga(estado),
        "hora": _hora(escenario.get("hora")),
        "cifras": cifras,
        "solidez": solidez_texto,
        "color": color,
        "supuestos": texto_supuestos(pesos.get("supuestos") or {}),
        "interpretacion": interpretacion,
        "con_explicacion": bool(explicacion),
        "consideraciones": consideraciones,
    }


def contenido(escenarios, fecha):
    """Todos los textos del informe, sin dibujar nada."""
    actual = escenarios[-1]["estado"]
    empresa = actual.get("empresa") or {}
    plantilla = empresa.get("plantilla_op")
    rot = (empresa.get("indicadores") or {}).get("rot_anual")
    todos = [(e["estado"].get("pesos") or {}).get("supuestos") or {} for e in escenarios]

    def supuesto(llave):
        valores = {s.get(llave) for s in todos}
        if len(valores) > 1:
            return "Varía por escenario"
        valor = valores.pop() if valores else None
        return "-" if valor is None else _pesos(valor)

    return {
        "empresa": str(empresa.get("id", "")),
        "fecha": fecha_larga(fecha),
        "titulo": f"Escenarios de compensación: {empresa.get('id', '')}",
        "subtitulo": f"{SUBTITULO} | {fecha_larga(fecha)}",
        "situacion": [
            ("Plantilla operativa", f"{plantilla:,} personas" if plantilla is not None else "-"),
            ("Rotación anual actual", f"{rot:.0%}" if rot is not None else "-"),
            ("Costo por baja *", supuesto("costo_por_baja")),
            ("Costo mensual por ruta *", supuesto("costo_ruta_mensual")),
        ],
        "introduccion": INTRODUCCION,
        "encabezados": ["N.º", "Escenario", "Con / sin", "Rotación anual", "Solidez", "Costo medida", "Brecha"],
        "filas": [fila(i, e["estado"]) for i, e in enumerate(escenarios, 1)],
        "detalles": [detalle(i, e) for i, e in enumerate(escenarios, 1)],
    }


def textos_con_cifras(datos, i):
    """Los textos del escenario i que deben salir de su estado (para el validador).

    Quedan fuera la interpretación (ya se validó cuando se escribió, contra su paso anterior),
    el número del escenario y la hora.
    """
    bloque = datos["detalles"][i]
    textos = [*datos["filas"][i]["celdas"][1:], bloque["titulo"], *(valor for _, valor in bloque["cifras"])]
    textos += [bloque["solidez"] or "", bloque["supuestos"], *(texto for _, texto in bloque["consideraciones"])]
    return textos


def _seguro(texto, estado):
    return texto if not cifras_inventadas(texto, estado) else SIN_DATO


def asegurar_cifras(datos, escenarios):
    """Pasa cada texto con cifras por el validador de la IA. Lo que no pasa se cambia por SIN_DATO.

    Las cifras son copias del estado, así que no debería fallar nunca; esto garantiza que, aun con un
    error futuro, el informe jamás imprima un número que no esté en los datos.
    """
    for i, escenario in enumerate(escenarios):
        estado = escenario["estado"]
        renglon = datos["filas"][i]
        renglon["celdas"] = [renglon["celdas"][0], *(_seguro(c, estado) for c in renglon["celdas"][1:])]
        bloque = datos["detalles"][i]
        bloque["titulo"] = _seguro(bloque["titulo"], estado)
        bloque["cifras"] = [(etiqueta, _seguro(valor, estado)) for etiqueta, valor in bloque["cifras"]]
        bloque["supuestos"] = _seguro(bloque["supuestos"], estado)
        bloque["consideraciones"] = [(tono, _seguro(texto, estado)) for tono, texto in bloque["consideraciones"]]
    ultimo = escenarios[-1]["estado"]
    datos["titulo"] = _seguro(datos["titulo"], ultimo)
    datos["situacion"] = [
        (etiqueta, valor if valor == "Varía por escenario" else _seguro(valor, ultimo))
        for etiqueta, valor in datos["situacion"]
    ]
    return datos


# ---------------------------------------------------------------------------
# 3. Estilo del informe (para cambiar el estilo, solo se tocan estos valores)
# ---------------------------------------------------------------------------
ENCABEZADO = "RADAR DE DECISIONES | COMPENSACIÓN OPERATIVA"
AZUL = (23, 43, 77)          # títulos, encabezado y líneas principales
TINTA = (38, 38, 38)         # texto
GRIS = (105, 105, 105)       # etiquetas y notas
GRIS_CLARO = (150, 150, 150)  # hora de registro
LINEA = (205, 205, 205)      # líneas finas
FONDO = (244, 245, 247)      # franjas de cifras
ROJO = (158, 30, 45)         # el grupo rota igual o más que el resto
MARCAS = {"verde": (46, 117, 70), "amarillo": (196, 146, 20), "naranja": (190, 96, 40)}  # solidez
SERIF, SANS = "Times", "Helvetica"
MARGEN = 20                  # mm, los cuatro lados
ANCHOS_TABLA = (7, 58, 19, 25, 30, 18, 19)  # mm; suman 176, el ancho útil de una hoja carta
ALINEACION_TABLA = ("L", "L", "C", "C", "L", "R", "R")


# Las fuentes que trae fpdf2 solo tienen los caracteres de latin-1 (acentos, ñ, ¿, ¡, «, », ·).
# Lo demás se cambia por algo equivalente antes de escribir, para que un texto con un guion largo
# o una flecha nunca rompa la descarga.
REEMPLAZOS = {
    "—": "-", "–": "-", "−": "-", "→": "->", "←": "<-", "≥": ">=", "≤": "<=", "≈": "aprox.",
    "“": '"', "”": '"', "‘": "'", "’": "'", "…": "...", "•": "·", "⚠": "", "↓": "", "↑": "",
    " ": " ", " ": " ",
}


def latin1(texto):
    """Deja el texto solo con caracteres que la fuente puede dibujar."""
    for viejo, nuevo in REEMPLAZOS.items():
        texto = texto.replace(viejo, nuevo)
    limpio = []
    for caracter in texto:
        if ord(caracter) < 256:
            limpio.append(caracter)
        else:  # último recurso: la letra sin su adorno (ŝ -> s) o nada
            limpio.append(unicodedata.normalize("NFKD", caracter).encode("latin-1", "ignore").decode("latin-1"))
    return re.sub(r"[ ]{2,}", " ", "".join(limpio))


def nombre_archivo(estado, fecha):
    """'Radar_COMPANIA-36_2026-10-21.pdf': sin acentos ni espacios, para que abra en cualquier equipo."""
    empresa = (estado.get("empresa") or {}).get("id") or "empresa"
    simple = unicodedata.normalize("NFKD", empresa).encode("ascii", "ignore").decode("ascii")
    simple = re.sub(r"[^A-Za-z0-9]+", "-", simple).strip("-") or "empresa"
    return f"Radar_{simple}_{fecha:%Y-%m-%d}.pdf"


def _hoja(empresa="", fecha=""):
    from fpdf import (
        FPDF,  # aquí y no arriba: si la librería falta, solo se apaga el botón
    )

    class Informe(FPDF):
        def header(self):
            self.set_y(11)
            self.set_font(SANS, size=7.5)
            self.set_text_color(*GRIS)
            self.cell(0, 4, latin1(ENCABEZADO), new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(*AZUL)
            self.set_line_width(0.5)
            self.line(self.l_margin, 16.5, self.w - self.r_margin, 16.5)
            self.set_line_width(0.2)
            self.set_y(22)

        def footer(self):
            self.set_y(-15)
            self.set_draw_color(*LINEA)
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
            self.ln(1.5)
            self.set_font(SANS, size=7.5)
            self.set_text_color(*GRIS)
            pie = " | ".join(p for p in (empresa, fecha, FUENTE) if p)
            self.cell(0, 4, latin1(pie), new_x="LMARGIN", new_y="TOP")
            self.cell(0, 4, f"Página {self.page_no()} de {{nb}}", align="R")

    pdf = Informe(format="letter", unit="mm")
    pdf.set_margins(MARGEN, MARGEN, MARGEN)
    pdf.set_auto_page_break(True, margin=MARGEN)
    pdf.set_title(latin1(f"Escenarios de compensación {empresa}".strip()))
    pdf.set_author("Radar de Decisiones")
    pdf.set_creator("Radar de Decisiones")
    pdf.add_page()
    return pdf


def _ajustar(pdf, fuente, tamano, texto, ancho, estilo=""):
    """Baja el tamaño de letra lo necesario para que el texto quepa en su casilla."""
    pdf.set_font(fuente, style=estilo, size=tamano)
    while pdf.get_string_width(texto) > ancho and tamano > 5:
        tamano -= 0.2
        pdf.set_font(fuente, style=estilo, size=tamano)


def _etiqueta(pdf, texto):
    pdf.set_font(SANS, style="B", size=8)
    pdf.set_text_color(*GRIS)
    pdf.cell(0, 5, latin1(texto.upper()), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.5)


def _seccion(pdf, numero, titulo):
    pdf.ln(4)
    pdf.set_font(SERIF, style="B", size=13)
    pdf.set_text_color(*AZUL)
    pdf.cell(0, 7, latin1(f"{numero}. {titulo}"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*LINEA)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(3)


def _franja(pdf, pares, alto=15):
    """Franja gris de cifras: etiqueta pequeña en mayúsculas y la cifra grande debajo. Nada se sale de su casilla."""
    ancho = (pdf.w - pdf.l_margin - pdf.r_margin) / len(pares)
    x0, y0 = pdf.l_margin, pdf.get_y()
    pdf.set_fill_color(*FONDO)
    pdf.rect(x0, y0, ancho * len(pares), alto, style="F")
    for i, (etiqueta, valor) in enumerate(pares):
        x, util = x0 + i * ancho, ancho - 7
        if i:
            pdf.set_draw_color(*LINEA)
            pdf.line(x, y0 + 2.5, x, y0 + alto - 2.5)
        texto = latin1(etiqueta.upper())
        _ajustar(pdf, SANS, 6.8, texto, util)
        pdf.set_text_color(*GRIS)
        pdf.set_xy(x + 3.5, y0 + 2.6)
        pdf.cell(util, 3.5, texto)
        texto = latin1(valor)
        _ajustar(pdf, SERIF, 13.5, texto, util)
        pdf.set_text_color(*TINTA)
        pdf.set_xy(x + 3.5, y0 + 7)
        pdf.cell(util, 6, texto)
    pdf.set_xy(pdf.l_margin, y0 + alto + 3)


def _parrafo(pdf, texto, tamano=10.5, estilo="", color=TINTA, interlinea=4.8, fuente=SERIF):
    pdf.set_font(fuente, style=estilo, size=tamano)
    pdf.set_text_color(*color)
    pdf.multi_cell(0, interlinea, latin1(texto), align="J", new_x="LMARGIN", new_y="NEXT")


def _tabla(pdf, datos):
    pdf.set_font(SANS, style="B", size=7.5)
    pdf.set_text_color(*AZUL)
    for ancho, titulo, alineacion in zip(ANCHOS_TABLA, datos["encabezados"], ALINEACION_TABLA, strict=True):
        pdf.cell(ancho, 6, latin1(titulo), align=alineacion)
    pdf.ln(6)
    pdf.set_draw_color(*AZUL)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    for renglon in datos["filas"]:
        celdas = [latin1(c) for c in renglon["celdas"]]
        pdf.set_font(SANS, size=8.3)
        lineas = pdf.multi_cell(ANCHOS_TABLA[1] - 2, 4.2, celdas[1], align="L", dry_run=True, output="LINES")
        alto = max(9, 4.2 * len(lineas) + 3.4)
        if pdf.will_page_break(alto):
            pdf.add_page()
        y, x = pdf.get_y(), pdf.l_margin
        pdf.set_text_color(*TINTA)
        pdf.set_xy(x, y)
        pdf.cell(ANCHOS_TABLA[0], alto, celdas[0])
        pdf.set_xy(x + ANCHOS_TABLA[0], y + 1.7)
        pdf.multi_cell(ANCHOS_TABLA[1] - 2, 4.2, celdas[1], align="L")
        x += ANCHOS_TABLA[0] + ANCHOS_TABLA[1]
        for i in (2, 3, 4, 5, 6):
            pdf.set_xy(x, y)
            pdf.set_text_color(*(ROJO if (i == 3 and renglon["rotan_mas"]) else TINTA))
            if i == 4 and renglon["color"]:  # cuadrito del color de la solidez, con la etiqueta escrita
                pdf.set_fill_color(*MARCAS[renglon["color"]])
                pdf.rect(x, y + alto / 2 - 1.1, 2.2, 2.2, style="F")
                pdf.set_xy(x + 3.6, y)
                pdf.cell(ANCHOS_TABLA[i] - 3.6, alto, celdas[i])
            else:
                pdf.cell(ANCHOS_TABLA[i], alto, celdas[i], align=ALINEACION_TABLA[i])
            x += ANCHOS_TABLA[i]
        pdf.set_y(y + alto)
        pdf.set_draw_color(*LINEA)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(2)
    _parrafo(pdf, NOTA_TABLA, tamano=7, color=GRIS, interlinea=3.6, fuente=SANS)


def _alto_bloque(pdf, bloque):
    """Cuánto mide el bloque de un escenario, para empezarlo en otra hoja si no cabe completo."""
    pdf.set_font(SERIF, style="B", size=11.5)
    titulo = pdf.multi_cell(0, 5.5, latin1(f"2.{bloque['numero']}  {bloque['titulo']}"), dry_run=True, output="HEIGHT")
    pdf.set_font(SERIF, size=10.5)
    texto = pdf.multi_cell(0, 4.8, latin1(bloque["interpretacion"]), dry_run=True, output="HEIGHT")
    pdf.set_font(SANS, size=8.8)
    ancho = pdf.w - pdf.l_margin - pdf.r_margin - 4
    consideraciones = sum(
        pdf.multi_cell(ancho, 4.6, latin1(t), dry_run=True, output="HEIGHT") for _, t in bloque["consideraciones"]
    )
    return 2 + titulo + 4 + 1.5 + 17 + 9.5 + 2 + 5.5 + texto + (7 + consideraciones if consideraciones else 0) + 4


def _bloque(pdf, bloque):
    if pdf.will_page_break(_alto_bloque(pdf, bloque)):
        pdf.add_page()
    pdf.ln(2)
    pdf.set_font(SERIF, style="B", size=11.5)
    pdf.set_text_color(*AZUL)
    pdf.multi_cell(0, 5.5, latin1(f"2.{bloque['numero']}  {bloque['titulo']}"), align="L",
                   new_x="LMARGIN", new_y="NEXT")
    if bloque["hora"]:
        pdf.set_font(SANS, size=7.5)
        pdf.set_text_color(*GRIS_CLARO)
        pdf.cell(0, 4, f"Escenario registrado a las {bloque['hora']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.5)
    _franja(pdf, bloque["cifras"], alto=14)
    for etiqueta, texto, color in (
        ("Solidez de la evidencia", bloque["solidez"], MARCAS.get(bloque["color"], TINTA)),
        ("Supuestos utilizados", bloque["supuestos"], TINTA),
    ):
        if not texto:
            continue
        pdf.set_font(SANS, style="B", size=8)
        pdf.set_text_color(*GRIS)
        pdf.cell(42, 4.5, latin1(etiqueta.upper()), new_x="RIGHT", new_y="TOP")
        pdf.set_font(SANS, size=8.8)
        pdf.set_text_color(*color)
        pdf.multi_cell(0, 4.5, latin1(texto), align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    _etiqueta(pdf, "Interpretación")
    _parrafo(pdf, bloque["interpretacion"], estilo="" if bloque["con_explicacion"] else "I")
    if bloque["consideraciones"]:
        pdf.ln(1.5)
        _etiqueta(pdf, "Consideraciones")
        pdf.set_font(SANS, size=8.8)
        for tono, texto in bloque["consideraciones"]:
            pdf.set_text_color(*(ROJO if tono == "rojo" else TINTA))
            pdf.cell(4, 4.6, "-", new_x="RIGHT", new_y="TOP")
            pdf.multi_cell(0, 4.6, latin1(texto), align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_draw_color(*LINEA)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(1)


def dibujar(datos):
    """Los textos de contenido() convertidos en un informe tamaño carta. Devuelve los bytes del PDF."""
    pdf = _hoja(datos["empresa"], datos["fecha"])
    pdf.set_font(SERIF, size=22)
    pdf.set_text_color(*AZUL)
    pdf.multi_cell(0, 10, latin1(datos["titulo"]), align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(SANS, size=9.5)
    pdf.set_text_color(*GRIS)
    pdf.cell(0, 5, latin1(datos["subtitulo"]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    _etiqueta(pdf, "Situación actual de la compañía")
    _franja(pdf, datos["situacion"])
    pdf.set_y(pdf.get_y() - 1.5)
    pdf.set_font(SANS, size=7)
    pdf.set_text_color(*GRIS)
    pdf.cell(0, 3.5, latin1(NOTA_SUPUESTOS), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    _parrafo(pdf, datos["introduccion"])

    _seccion(pdf, 1, "Resumen de escenarios")
    _tabla(pdf, datos)
    if datos["detalles"] and pdf.will_page_break(20 + _alto_bloque(pdf, datos["detalles"][0])):
        pdf.add_page()  # que el título de la sección no quede solo al final de la hoja
    _seccion(pdf, 2, "Detalle por escenario")
    for bloque in datos["detalles"]:
        _bloque(pdf, bloque)
    if pdf.will_page_break(35):
        pdf.add_page()
    _seccion(pdf, 3, "Nota metodológica")
    _parrafo(pdf, METODOLOGIA, tamano=8, color=GRIS, interlinea=4, fuente=SANS)
    return bytes(pdf.output())


def pdf_de_aviso():
    """Un PDF de una hoja con el aviso de falla: si algo sale mal, se baja esto y no un archivo roto."""
    pdf = _hoja()
    pdf.set_font(SERIF, size=18)
    pdf.set_text_color(*AZUL)
    pdf.cell(0, 9, "Radar de Decisiones", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    _parrafo(pdf, AVISO_FALLA, tamano=11)
    return bytes(pdf.output())


def armar_pdf(estado, guardados, texto_actual=None, fecha=None):
    """Todo junto: escenarios -> textos -> validación -> PDF. Devuelve (bytes del PDF, cuántos escenarios lleva)."""
    fecha = fecha or datetime.now().astimezone()
    escenarios = escenarios_para_resumen(estado, guardados, texto_actual)
    datos = asegurar_cifras(contenido(escenarios, fecha), escenarios)
    return dibujar(datos), len(escenarios)
