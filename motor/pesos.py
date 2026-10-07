"""Costo de la medida y costo de rotar más que el grupo. Dueño: Juanes.

Regla acordada: los costos de aguinaldo, prima y vales se calculan siempre con el
salario diario inicial ACTUAL de la empresa, aunque también se haya movido el salario.
"""

DIAS_VACACIONES = 12
DIAS_ANIO = 365
MESES_ANIO = 12


def costo_medida(perfil, palancas_movidas, supuestos):
    """Costo anual en pesos de llevar cada palanca movida de su valor actual al nuevo.

    perfil: dict con "plantilla_op" y "palancas" (valores actuales de la empresa).
    palancas_movidas: dict {palanca: valor nuevo}.
    supuestos: dict con "costo_ruta_mensual" (solo se usa si se mueven las rutas).
    Devuelve la suma; si una palanca baja, su parte es negativa (la medida ahorra).
    """
    actual = perfil["palancas"]
    plantilla = perfil["plantilla_op"]
    salario = actual["sal_dia_ini"]
    total = 0.0
    for palanca, nuevo in palancas_movidas.items():
        delta = nuevo - actual[palanca]
        if palanca == "sal_dia_ini":
            total += delta * DIAS_ANIO * plantilla
        elif palanca == "aguinaldo_op":
            total += delta * salario * plantilla
        elif palanca == "prima_vac_op":
            total += delta * DIAS_VACACIONES * salario * plantilla
        elif palanca == "vales_op":
            total += delta * salario * DIAS_ANIO * plantilla
        elif palanca == "rutas_x100":
            rutas_extra = delta * plantilla / 100
            total += rutas_extra * supuestos["costo_ruta_mensual"] * MESES_ANIO
        else:
            raise ValueError(f"Palanca desconocida: {palanca}")
    return total


def costo_brecha(rot_empresa, rot_grupo, plantilla, costo_por_baja):
    """Costo anual de rotar más que el grupo. Devuelve 0 si la empresa ya rota menos."""
    return max(0.0, rot_empresa - rot_grupo) * plantilla * costo_por_baja
