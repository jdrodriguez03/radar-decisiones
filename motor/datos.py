"""Carga de empresas.parquet."""
#Se cargan los datos de las empresas desde el archivo Parquet y se valida su integridad.
#verificando las 40 filas, la columna 'empresa' y las columnas de palancas definidas en config.PALANCAS.
import pandas as pd

from config import PALANCAS, RUTA_EMPRESAS


def cargar() -> pd.DataFrame:
    """Carga y valida el DataFrame de 40 empresas desde el Parquet."""
    empresas = pd.read_parquet(RUTA_EMPRESAS)

    if len(empresas) != 40:
        raise ValueError(f"Se esperaban 40 empresas; se encontraron {len(empresas)}.")
    if "empresa" not in empresas.columns:
        raise ValueError("Falta la columna requerida 'empresa' en el Parquet.")
    if empresas["empresa"].isna().any() or empresas["empresa"].duplicated().any():
        raise ValueError("El Parquet debe contener 40 empresas identificadas sin duplicados.")

    faltantes = set(PALANCAS).difference(empresas.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas de palancas en el Parquet: {sorted(faltantes)}")

    return empresas


