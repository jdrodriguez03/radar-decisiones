"""Genera el informe de calidad de empresas.parquet."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from config import PALANCAS, RUTA_EMPRESAS
from motor.datos import cargar
#Se define la ruta del informe de calidad de datos y una lista de empresas que requieren confirmación con Recursos Humanos.
RUTA_INFORME = RAIZ / "docs" / "calidad_datos.md"
EMPRESAS_POR_CONFIRMAR_RH = (
    "COMPAÑIA 4",
    "COMPAÑIA 7",
    "COMPAÑIA 9",
    "COMPAÑIA 20",
    "COMPAÑIA 26",
    "COMPAÑIA 35",
)

#presentación de los valores numéricos con cuatro decimales, eliminando ceros y puntos finales innecesarios.
def _formato_numero(valor: float) -> str:
    return f"{valor:.4f}".rstrip("0").rstrip(".")

#se genera un informe en formato Markdown que incluye la fuente de datos, 
# el número de empresas, los valores faltantes por columna, 
# los percentiles de las palancas y las empresas que requieren 
# confirmación con Recursos Humanos.
def generar_informe(empresas: pd.DataFrame) -> str:
    faltantes = empresas.isna().sum()
    lineas = [
        "# Calidad de datos de empresas",
        "",
        f"Fuente: `{RUTA_EMPRESAS.relative_to(RAIZ).as_posix()}`.",
        f"Empresas: {len(empresas)}; identificadores únicos: {empresas['empresa'].nunique()}.",
        "",
        "## Valores faltantes por columna",
        "",
        "| Columna | Faltantes |",
        "|---|---:|",
    ]
    lineas.extend(f"| `{columna}` | {cantidad} |" for columna, cantidad in faltantes.items())
    lineas.extend(
        [
            "",
            "## Percentiles de las cinco palancas",
            "",
            "Se comparan P5 y P95 observados con los límites de controles definidos en `config.PALANCAS`.",
            "Los conteos fuera de rango usan los valores de las empresas y límites inclusivos.",
            "",
            "| Palanca | Válidos | P5 | P95 | Rango del control | Bajo | Sobre |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for palanca, (minimo, maximo, _paso) in PALANCAS.items():
        valores = pd.to_numeric(empresas[palanca], errors="coerce")
        validos = valores.dropna()
        bajo = int(validos.lt(minimo).sum())
        sobre = int(validos.gt(maximo).sum())
        p5 = _formato_numero(float(validos.quantile(0.05))) if not validos.empty else "N/D"
        p95 = _formato_numero(float(validos.quantile(0.95))) if not validos.empty else "N/D"
        lineas.append(
            f"| `{palanca}` | {len(validos)} | {p5} | {p95} | "
            f"{_formato_numero(minimo)}–{_formato_numero(maximo)} | {bajo} | {sobre} |"
        )

    minimo_salario = PALANCAS["sal_dia_ini"][0]
    bajo_control = empresas.loc[
        pd.to_numeric(empresas["sal_dia_ini"], errors="coerce").lt(minimo_salario),
        ["empresa", "sal_dia_ini"],
    ].sort_values("empresa")
    lineas.extend(
        [
            "",
            "## Salarios iniciales bajo el límite inferior del control",
            "",
            (
                f"El límite inferior configurado para `sal_dia_ini` es ${minimo_salario:.2f} diarios. "
                "Esto identifica valores bajo el rango del control de la aplicación; **no determina "
                "por sí solo incumplimiento del salario mínimo legal**."
            ),
            "",
        ]
    )
    if bajo_control.empty:
        lineas.append("No hay empresas bajo ese límite.")
    else:
        lineas.extend(
            [
                "| Empresa | Mediana de salario diario inicial |",
                "|---|---:|",
            ]
        )
        lineas.extend(
            f"| {fila.empresa} | ${fila.sal_dia_ini:.2f} |"
            for fila in bajo_control.itertuples(index=False)
        )

    lineas.extend(
        [
            "",
            "## Confirmación pendiente con RH",
            "",
            (
                "La lista pendiente en `docs/decisiones.md` incluye las empresas siguientes. "
                "Se reportan sus medianas para facilitar la revisión; la comparación legal debe "
                "considerar el periodo de cada dato y el salario mínimo aplicable en ese periodo."
            ),
            "",
            "| Empresa | Mediana de salario diario inicial |",
            "|---|---:|",
        ]
    )
    por_confirmar = empresas.loc[
        empresas["empresa"].isin(EMPRESAS_POR_CONFIRMAR_RH),
        ["empresa", "sal_dia_ini"],
    ].sort_values("empresa")
    lineas.extend(
        f"| {fila.empresa} | ${fila.sal_dia_ini:.2f} |"
        for fila in por_confirmar.itertuples(index=False)
    )
    lineas.append("")
    return "\n".join(lineas)

# se define la función principal que genera el informe de calidad de datos 
# y lo guarda en un archivo Markdown.
def main() -> None:
    informe = generar_informe(cargar())
    RUTA_INFORME.parent.mkdir(parents=True, exist_ok=True)
    RUTA_INFORME.write_text(informe, encoding="utf-8")
    print(f"Informe guardado: {RUTA_INFORME}")

# se ejecuta la función principal si el script se ejecuta directamente.
if __name__ == "__main__":
    main()
