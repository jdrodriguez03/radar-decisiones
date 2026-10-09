"""Texto de respaldo cuando la API falla o tarda. Dueño: Julian."""


def fmt_pct(x):
    """0.222 -> '22%'"""
    return f"{x:.0%}"


def fmt_pesos(x):
    """6341580 -> '$6.3 millones'; menos de un millón -> '$850,000'"""
    if x >= 1_000_000:
        return f"${x / 1_000_000:.1f} millones"
    return f"${x:,.0f}"


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



def _plantilla_inicial(estado):
    """Texto cuando el usuario aún no mueve ninguna palanca (estado inicial o Restablecer)."""
    empresa = estado["empresa"]["indicadores"]["rot_anual"]
    grupo = estado["grupo"]
    return (
        f"Hoy su empresa pierde {fmt_pct(empresa)} de su plantilla al año; "
        f"la empresa típica entre las {grupo['n']} empresas de la encuesta pierde {fmt_pct(grupo['indicadores']['rot_anual'])}. "
        f"Mueva una palanca para ver qué muestran las empresas que ya la aplican."
    )


def plantilla(estado):
    cambio = estado.get("cambio")
    if not cambio:
        return _plantilla_inicial(estado)
    grupo = estado["grupo"]
    resto = estado["resto"]
    pesos = estado["pesos"]

    primera = (
        f"Al llevar {nombre_palanca(cambio['palanca'], cambio['a'])}, "
        f"su grupo queda en {grupo['n']} empresas que pierden "
        f"{fmt_pct(grupo['indicadores']['rot_anual'])} de su plantilla al año, "
        f"frente a {fmt_pct(resto['indicadores']['rot_anual'])} "
        f"de las {resto['n']} restantes."
    )

    medida = fmt_pesos(pesos["costo_medida_anual"])
    if pesos["costo_brecha_anual"] <= 0:
        segunda = f"Su empresa ya rota menos que este grupo; la medida costaría {medida} al año."
    else:
        segunda = (
            f"Rotar como ese grupo representa {fmt_pesos(pesos['costo_brecha_anual'])} "
            f"al año, contra {medida} de la medida."
        )

    return f"{primera} {segunda}"
