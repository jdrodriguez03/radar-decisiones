"""Data preparation script for the radar-decisiones project."""
#Se preparan las rutas y trae los datos de la base reducida, se agregan por empresa y se guardan en un archivo parquet.
#Se preparan las rutas y trae las reglas compartidas 
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from config import ESCALA_MOTIVOS, RUTA_EMPRESAS, RUTA_XLSX  
# Se define una función para calcular la moda de una serie de pandas, devolviendo el primer valor de la moda si existe, o pd.NA si no hay moda.
def _moda(valores: pd.Series) -> object:
    modas = valores.mode(dropna=True)
    return modas.iloc[0] if not modas.empty else pd.NA
#Lee la base de datos desde un archivo Excel, 
#valida que contenga las columnas requeridas y que no haya filas sin empresa.
#Luego, convierte los valores de las columnas de motivos según una escala predefinida, 
#agregando los datos por empresa y calculando la rotación anual y la banda de plantilla. 
# Finalmente, devuelve un DataFrame con los datos preparados.
def preparar_datos() -> pd.DataFrame:
    df = pd.read_excel(RUTA_XLSX, sheet_name="BASE_REDUCIDA")

    columnas_requeridas = {"empresa", "rot_vol_op", "plantilla_op"}
    faltantes = columnas_requeridas.difference(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas en BASE_REDUCIDA: {sorted(faltantes)}")
    if df["empresa"].isna().any():
        raise ValueError("Hay filas sin empresa en BASE_REDUCIDA.")

    motivos = [col for col in df.columns if col.startswith("m_")]
    for columna in motivos:
        valores = df[columna]
        convertidos = valores.map(ESCALA_MOTIVOS)
        invalidos = valores.notna() & convertidos.isna()
        if invalidos.any():
            raise ValueError(
                f"Valores fuera de la escala de motivos en {columna}: "
                f"{sorted(valores[invalidos].unique().tolist())}"
            )
        df[columna] = convertidos

    columnas_numericas = [
        col for col in df.select_dtypes(include="number").columns if col != "empresa"
    ]
    columnas_texto = [
        col for col in df.columns if col != "empresa" and col not in columnas_numericas
    ]
    agregaciones = {col: "median" for col in columnas_numericas}
    agregaciones.update({col: _moda for col in columnas_texto})

    empresas = df.groupby("empresa", as_index=False).agg(agregaciones)
    empresas["rot_anual"] = empresas["rot_vol_op"] * 12

    plantilla = empresas["plantilla_op"]
    empresas["banda"] = pd.Series(pd.NA, index=empresas.index, dtype="string")
    empresas.loc[plantilla.le(186), "banda"] = "chica"
    empresas.loc[plantilla.between(202, 570), "banda"] = "mediana"
    empresas.loc[plantilla.ge(627), "banda"] = "grande"
    return empresas

#Se comprueba que el número de empresas sea 40 y que la mediana de rot_anual sea 0.36, 
# guardando los datos en un archivo parquet si las condiciones se cumplen.
def main() -> None:
    empresas = preparar_datos()
    if len(empresas) != 40:
        raise ValueError(f"Se esperaban 40 empresas; se obtuvieron {len(empresas)}.")

    mediana_rotacion = empresas["rot_anual"].median()
    if round(float(mediana_rotacion), 2) != 0.37:
        raise ValueError(
            f"Se esperaba una mediana de rot_anual de 0.37; se obtuvo {mediana_rotacion:.2f}."
        )
    empresas.to_parquet(RUTA_EMPRESAS, index=False)
    print(f"Guardado: {RUTA_EMPRESAS} ({len(empresas)} empresas)")
    print(f"Mediana de rot_anual: {mediana_rotacion:.2f}")

# se ejecuta la función main si el script se ejecuta directamente, 
# permitiendo que el script se use como módulo sin ejecutar la preparación de datos automáticamente.
if __name__ == "__main__":
    main()
