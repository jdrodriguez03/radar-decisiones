"""Texto de respaldo cuando la IA no puede dar una explicación válida. Dueño: Julian.

Sale cuando no hay internet, la IA tarda, la API falla o la IA escribe una cifra que no
está en los datos. Por eso habla igual que el prompt: mismas tres oraciones, mismas reglas
de lenguaje, solo cifras del JSON (o de ia/derivadas.py) y nunca promete resultados.
"""
from ia.derivadas import cifras_derivadas
from ia.prompts import como_decirlo, rasgos_utiles


def fmt_pct(x):
    """0.222 -> '22%'"""
    return f"{x:.0%}"


def fmt_pesos(x):
    """6341580 -> '$6.3 millones'; menos de un millón -> '$850,000'"""
    if x >= 1_000_000:
        return f"${x / 1_000_000:.1f} millones"
    return f"${x:,.0f}"


def _pesos_texto(x):
    """'$6.3 millones de pesos' o '$850,000 pesos'."""
    return f"{fmt_pesos(x)} de pesos" if x >= 1_000_000 else f"{fmt_pesos(x)} pesos"


def nombre_palanca(palanca, valor):
    """('aguinaldo_op', 20) -> 'el aguinaldo a 20 días'"""
    nombres = {
        "sal_dia_ini": lambda v: f"el salario inicial a ${v:,.0f}",
        "aguinaldo_op": lambda v: f"el aguinaldo a {v:g} días",
        "prima_vac_op": lambda v: f"la prima vacacional a {v:.0%}",
        "vales_op": lambda v: f"los vales de despensa a {v * 100:g}%",
        "rutas_x100": lambda v: f"las rutas a {v:g} por cada 100 operativos",
    }
    return nombres[palanca](valor)


def _en_lista(partes):
    """['a', 'b', 'c'] -> 'a, b y c'"""
    return partes[0] if len(partes) == 1 else f"{', '.join(partes[:-1])} y {partes[-1]}"


def _plantilla_inicial(estado):
    """Sin palancas movidas (estado inicial o Restablecer): el tamaño del problema y una invitación."""
    empresa = estado["empresa"]["indicadores"]["rot_anual"]
    grupo = estado["grupo"]
    derivadas = cifras_derivadas(estado)
    personas = derivadas.get("personas_que_pierde_al_año")
    tempranas = derivadas.get("personas_que_se_van_antes_de_3_meses")

    primera = f"Hoy su empresa pierde {fmt_pct(empresa)} de su plantilla al año"
    if personas:
        primera += f", unas {personas['valor']} personas"
        if tempranas:
            primera += f", y unas {tempranas['valor']} se van antes de cumplir 3 meses"
    primera += "."
    segunda = (
        f"La empresa típica entre las {grupo['n']} empresas de la encuesta pierde "
        f"{fmt_pct(grupo['indicadores']['rot_anual'])}."
    )
    tercera = "Mueva una palanca para ver qué muestran las empresas que ya la aplican."
    return f"{primera} {segunda} {tercera}"


def _aviso_o_rasgo(estado):
    """La tercera oración: primero las advertencias; si la señal es clara, un rasgo en común."""
    grupo = estado["grupo"]
    etiqueta = (estado.get("senal") or {}).get("etiqueta")
    if grupo.get("completado"):
        return "El grupo se completó con empresas parecidas, así que conviene tomar esta comparación con cautela."
    if etiqueta == "no concluyente":
        return "La señal no es concluyente: conviene tomar esta comparación con cautela."
    if etiqueta == "débil":
        return "La señal es débil: conviene tomar esta comparación con cautela."
    rasgos = rasgos_utiles(estado)
    if not rasgos:
        return ""
    rasgo = rasgos[0]
    como = como_decirlo(rasgo)
    if isinstance(rasgo.get("grupo"), str):  # conteo como "16 de 22": "la mayoría ... también tiene"
        return f"Además, {como} de esas empresas también tiene {rasgo['texto']}."
    texto = rasgo.get("texto", "")
    if texto.endswith(" mediano") and como.startswith("suelen tener un valor más "):
        direccion = como.removeprefix("suelen tener un valor más ").split(" ")[0]  # "alto" o "bajo"
        return f"Además, esas empresas suelen tener un {texto.removesuffix(' mediano')} más {direccion} que las demás."
    return ""  # un rasgo que no se sabe decir bien se omite: mejor dos oraciones claras que tres raras


def plantilla(estado):
    if not estado.get("cambio"):
        return _plantilla_inicial(estado)
    grupo = estado["grupo"]
    resto = estado["resto"]
    pesos = estado["pesos"]
    movidas = estado.get("palancas_movidas") or {estado["cambio"]["palanca"]: estado["cambio"]["a"]}

    palancas = _en_lista([f"{nombre_palanca(p, v)} o más" for p, v in movidas.items()])
    primera = (
        f"Las {grupo['n']} empresas que ya tienen {palancas} pierden "
        f"{fmt_pct(grupo['indicadores']['rot_anual'])} de su plantilla al año; "
        f"las demás, {fmt_pct(resto['indicadores']['rot_anual'])}."
    )

    medida = _pesos_texto(pesos["costo_medida_anual"])
    if pesos["costo_brecha_anual"] <= 0:
        segunda = (
            "Su empresa ya pierde igual o menos gente al año que esas empresas, por lo que no hay "
            f"diferencia en pesos a su favor; la medida costaría {medida} al año."
        )
    else:
        segunda = (
            f"Para su empresa, esa diferencia equivale a {_pesos_texto(pesos['costo_brecha_anual'])} "
            f"al año en bajas, contra {medida} que costaría la medida."
        )

    return " ".join(parte for parte in (primera, segunda, _aviso_o_rasgo(estado)) if parte)
