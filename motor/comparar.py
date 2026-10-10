"""Universo, grupo, resto, completado a 5 y señal. Dueño: Aleja."""
from __future__ import annotations

from math import isfinite
from numbers import Real

import pandas as pd
from scipy.stats import mannwhitneyu
from sklearn.neighbors import NearestNeighbors

from config import MIN_GRUPO, PALANCAS

#Set de indicadores que se usarán para calcular medianas y señal.
INDICADORES = {
    "rot_anual": "rot_anual",
    "rot_temprana": "bajas_menos3m",
    "ausentismo": "aus_inj_op",
}

# función para resumir el tamaño, los identificadores y 
# las medianas de los indicadores para un DataFrame dado. 
def resumen(df: pd.DataFrame) -> dict:
    """Resume el tamaño, los identificadores y las medianas para el contrato."""
    if df.empty:
        return {"n": 0, "ids": [], "indicadores": None}

    faltantes = set(INDICADORES.values()).difference(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas de indicadores: {sorted(faltantes)}")

    indicadores = {}
    for nombre, columna in INDICADORES.items():
        mediana = df[columna].median()
        indicadores[nombre] = None if pd.isna(mediana) else float(mediana)

    return {
        "n": len(df),
        "ids": sorted(df["empresa"].astype(str).tolist()),
        "indicadores": indicadores,
    }

# función para completar el grupo con empresas similares según las palancas movidas.
def completar_con_similares(
    universo: pd.DataFrame,
    palancas_movidas: dict[str, float],
    k: int = MIN_GRUPO,
) -> pd.DataFrame:
    """Devuelve hasta k empresas más cercanas en las palancas movidas."""
    if k < 1:
        raise ValueError("k debe ser al menos 1.")
    if not palancas_movidas:
        raise ValueError("Se necesita al menos una palanca movida para buscar similares.")
    desconocidas = set(palancas_movidas).difference(PALANCAS)
    if desconocidas:
        raise ValueError(f"Palancas desconocidas: {sorted(desconocidas)}")

    faltantes = set(palancas_movidas).difference(universo.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas de palancas en el universo: {sorted(faltantes)}")
    if universo.empty:
        return universo.copy()

    columnas = list(palancas_movidas)
    candidatos = universo.dropna(subset=columnas)
    if candidatos.empty:
        return candidatos.copy()

    escalas = pd.Series(
        {columna: PALANCAS[columna][1] - PALANCAS[columna][0] for columna in columnas},
        dtype=float,
    )
    matriz = candidatos[columnas].astype(float).div(escalas, axis="columns")
    objetivo = pd.DataFrame([palancas_movidas], columns=columnas).astype(float)
    objetivo = objetivo.div(escalas, axis="columns")
# Se utiliza NearestNeighbors para encontrar las k empresas más cercanas en el espacio de las palancas movidas.
    vecinos = NearestNeighbors(n_neighbors=min(k, len(candidatos)))
    vecinos.fit(matriz)
    distancias, indices = vecinos.kneighbors(objetivo)
    cercanos = candidatos.iloc[indices[0]].copy()
    cercanos["_distancia"] = distancias[0]
    cercanos = cercanos.sort_values(["_distancia", "empresa"], kind="stable")
    return cercanos.drop(columns="_distancia")

# función para calcular la señal de Mann–Whitney entre el grupo y el resto.
#Para ver si hay diferencias significativas en la rotación anual entre el grupo y el resto.
def senal(grupo: pd.DataFrame, resto: pd.DataFrame) -> dict:
    """Calcula Mann–Whitney de rotación anual y etiqueta su p-valor."""
    if grupo.empty or resto.empty:
        return {"etiqueta": "no aplica", "p": None}
    if "rot_anual" not in grupo or "rot_anual" not in resto:
        raise ValueError("Ambos grupos deben incluir la columna 'rot_anual'.")

    valores_grupo = grupo["rot_anual"].dropna()
    valores_resto = resto["rot_anual"].dropna()
    if valores_grupo.empty or valores_resto.empty:
        return {"etiqueta": "no aplica", "p": None}

    p = float(
        mannwhitneyu(
            valores_grupo,
            valores_resto,
            alternative="two-sided",
            method="auto",
        ).pvalue
    )
    if p < 0.05:
        etiqueta = "clara"
    elif p < 0.15:
        etiqueta = "débil"
    else:
        etiqueta = "no concluyente"
    return {"etiqueta": etiqueta, "p": p}

# función principal para comparar una empresa con el universo y generar el grupo, resto, medianas y señal.
def comparar(
    empresas: pd.DataFrame,
    empresa_id: str,
    palancas_movidas: dict[str, float],
    solo_tamano: bool = False,
) -> dict:
    """Construye el universo elegible, grupo, resto, medianas y señal."""
    if "empresa" not in empresas:
        raise ValueError("Falta la columna requerida 'empresa'.")
    seleccionada = empresas.loc[empresas["empresa"].eq(empresa_id)]
    if len(seleccionada) != 1:
        raise ValueError(f"Se esperaba una empresa '{empresa_id}'; se encontraron {len(seleccionada)}.")
    if not isinstance(palancas_movidas, dict):
        raise TypeError("palancas_movidas debe ser un diccionario.")
    desconocidas = set(palancas_movidas).difference(PALANCAS)
    if desconocidas:
        raise ValueError(f"Palancas desconocidas: {sorted(desconocidas)}")
    for palanca, valor in palancas_movidas.items():
        if not isinstance(valor, Real) or isinstance(valor, bool) or not isfinite(float(valor)):
            raise ValueError(f"El nivel de {palanca} debe ser un número finito.")
# Se construye el universo de empresas excluyendo la empresa seleccionada y filtrando por tamaño si es necesario.
    universo = empresas.loc[empresas["empresa"].ne(empresa_id)].copy()
    if solo_tamano:
        if "banda" not in empresas:
            raise ValueError("Falta la columna 'banda' necesaria para filtrar por tamaño.")
        banda = seleccionada.iloc[0]["banda"]
        if pd.isna(banda):
            raise ValueError(f"La empresa '{empresa_id}' no tiene una banda de tamaño definida.")
        universo = universo.loc[universo["banda"].eq(banda)]
# Se filtra el universo según las palancas movidas y se separa en grupo y resto.
    columnas_movidas = list(palancas_movidas)
    faltantes = set(columnas_movidas).difference(universo.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas de palancas en el DataFrame: {sorted(faltantes)}")
    if columnas_movidas:
        universo = universo.dropna(subset=columnas_movidas)
# Se crea una máscara booleana para identificar las empresas que cumplen con los niveles de las palancas movidas.
    mascara_grupo = pd.Series(True, index=universo.index)
    for palanca, nivel in palancas_movidas.items():
        mascara_grupo &= universo[palanca].ge(nivel)
    grupo = universo.loc[mascara_grupo].copy()
    resto = universo.loc[~mascara_grupo].copy()
# Se verifica si el grupo es menor que el tamaño mínimo y se completa con empresas similares si es necesario.
    completado = len(grupo) < MIN_GRUPO
    if completado and palancas_movidas:
        grupo = completar_con_similares(universo, palancas_movidas, MIN_GRUPO)
        resto = universo.loc[~universo.index.isin(grupo.index)].copy()

    return {
        "grupo": resumen(grupo),
        "resto": resumen(resto),
        "completado": completado,
        "senal": senal(grupo, resto),
    }
