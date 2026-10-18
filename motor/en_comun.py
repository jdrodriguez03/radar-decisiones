"""Diferencias principales entre grupo y resto. Dueño: Aleja."""
from __future__ import annotations

from math import sqrt
from numbers import Integral

import pandas as pd
from pandas.api.types import is_numeric_dtype

from config import PALANCAS

#se define un diccionario NOMBRES_CONTEXTO que mapea nombres de columnas a descripciones legibles. Esto se utiliza para generar salidas más comprensibles al reportar diferencias entre grupos de datos.
NOMBRES_CONTEXTO = {
    "sal_dia_ini": "salario inicial mediano",
    "aguinaldo_op": "aguinaldo mediano",
    "prima_vac_op": "prima vacacional de 50% o más",
    "vales_op": "vales de despensa medianos",
    "rutas_x100": "rutas por cada 100 operativos medianas",
    "fondo_op": "fondo de ahorro mediano",
    "comedor": "ofrecen comedor",
    "jornada_12h": "manejan jornadas de 12 horas",
    "m_sueldo": "motivo de baja: mejor sueldo",
    "m_prest": "motivo de baja: mejores prestaciones",
    "m_ruta": "motivo de baja: mejor ruta de transporte",
    "m_cerca": "motivo de baja: empleo más cerca de casa",
    "m_horario": "motivo de baja: mejor horario",
    "m_horcomp": "motivo de baja: horario complicado",
    "m_companeros": "motivo de baja: problemas con compañeros",
    "m_jefe": "motivo de baja: problemas con el supervisor",
    "m_rendimiento": "motivo de baja: bajo rendimiento",
    "m_fin_contrato": "motivo de baja: fin de contrato",
    "m_residencia": "motivo de baja: cambio de residencia",
    "m_familia": "motivo de baja: conflictos familiares",
    "m_enfermedad": "motivo de baja: enfermedad",
    "m_estudios": "motivo de baja: estudios",
    "m_negocio": "motivo de baja: iniciar negocio propio",
    "m_inseguridad": "motivo de baja: inseguridad en la zona",
    "m_cuidados": "motivo de baja: cuidado de hijos o familiares",
    "m_personales": "motivo de baja: motivos personales",
}
# se crea función de utilidad para determinar si un valor es "sí" o "no" en diferentes formatos, incluyendo booleanos y cadenas de texto. Esto permite contar correctamente los valores "sí" en las columnas relevantes.
def _es_si(valor: object) -> bool:
    if isinstance(valor, bool):
        return valor
    return str(valor).strip().casefold().replace("í", "i") in {"si", "yes", "true"}

# se define una función interna _conteo_si que cuenta cuántos valores "sí" hay en dos series de datos (grupo y resto) y calcula la proporción de "sí" en cada grupo,
#  así como una puntuación basada en la diferencia de proporciones y el error estándar. 
# Esta función también valida los valores inesperados en las columnas de tipo Sí/No.
def _conteo_si(
    columna: str,
    grupo: pd.Series,
    resto: pd.Series,
) -> tuple[dict[str, str], float] | None:
    valores_grupo = [valor for valor in grupo.tolist() if not pd.isna(valor)]
    valores_resto = [valor for valor in resto.tolist() if not pd.isna(valor)]
    if not valores_grupo and not valores_resto:
        return None

    def normalizar(valor: object) -> str:
        return str(valor).strip().casefold().replace("í", "i")

    normalizados = [
        normalizar(valor) for valor in (*valores_grupo, *valores_resto)
    ]
    permitidos = {"si", "no", "yes", "true", "false"}
    inesperados = set(normalizados).difference(permitidos)
    if inesperados:
        raise ValueError(
            f"Valores no reconocidos en la columna Sí/No {columna}: {sorted(inesperados)}"
        )

    si = {"si", "yes", "true"}
    cuenta_g = sum(valor in si for valor in normalizados[: len(valores_grupo)])
    cuenta_r = sum(valor in si for valor in normalizados[len(valores_grupo) :])
    proporcion_g = cuenta_g / len(valores_grupo) if valores_grupo else 0.0
    proporcion_r = cuenta_r / len(valores_resto) if valores_resto else 0.0

    p_comun = (cuenta_g + cuenta_r) / (len(valores_grupo) + len(valores_resto))
    error_estandar = sqrt(
        p_comun
        * (1 - p_comun)
        * (1 / len(valores_grupo) + 1 / len(valores_resto))
    ) if valores_grupo and valores_resto else 0.0
    puntuacion = abs(proporcion_g - proporcion_r) / error_estandar if error_estandar else 0.0
    return (
        {
            "grupo": f"{cuenta_g} de {len(valores_grupo)}",
            "resto": f"{cuenta_r} de {len(valores_resto)}",
        },
        puntuacion,
    )


def _a_numerico(df: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    dtypes = df.dtypes
    if all(is_numeric_dtype(dtypes[columna]) for columna in columnas):
        return df[columnas]
    return df[columnas].apply(pd.to_numeric, errors="coerce")


# se define la función diferencias_principales que compara dos grupos de datos (grupo y resto) 
# y devuelve los n rasgos más distintos entre ellos. La función calcula diferencias en proporciones 
# para columnas de tipo Sí/No y diferencias en medianas para columnas numéricas, utilizando desviaciones 
# estándar para normalizar las diferencias. También permite excluir ciertas palancas del análisis y usar un 
# conjunto de referencia para calcular desviaciones estándar si se proporciona.
def diferencias_principales(
    grupo: pd.DataFrame,
    resto: pd.DataFrame,
    n: int = 2,
    *,
    palancas_movidas: dict[str, float] | None = None,
    referencia: pd.DataFrame | None = None,
) -> list[dict[str, str | float]]:
    """Devuelve los n rasgos más distintos con el formato de en_comun del contrato.

    Si se proporciona, referencia contiene las 40 empresas para calcular desviaciones
    estándar; sin ella se usa el conjunto combinado de grupo y resto.
    """
    if not isinstance(n, Integral) or isinstance(n, bool) or n < 0:
        raise ValueError("n debe ser un entero mayor o igual a cero.")
    if n == 0 or grupo.empty or resto.empty:
        return []
    if "empresa" not in grupo.columns or "empresa" not in resto.columns:
        raise ValueError("Grupo y resto deben incluir la columna 'empresa'.")
    palancas_movidas = palancas_movidas or {}
    desconocidas = set(palancas_movidas).difference(PALANCAS)
    if desconocidas:
        raise ValueError(f"Palancas desconocidas: {sorted(desconocidas)}")

    contexto = [
        *PALANCAS,
        "comedor",
        "jornada_12h",
        "fondo_op",
        *sorted(columna for columna in grupo.columns if columna.startswith("m_")),
    ]
    columnas = [
        columna
        for columna in contexto
        if columna not in palancas_movidas
        and columna in grupo.columns
        and columna in resto.columns
    ]
    referencia_numerica = (
        pd.concat([grupo, resto], ignore_index=True)
        if referencia is None
        else referencia
    )
    columnas_numericas = [
        columna
        for columna in columnas
        if columna not in {"comedor", "jornada_12h"}
    ]
    grupo_numerico = _a_numerico(grupo, columnas_numericas)
    resto_numerico = _a_numerico(resto, columnas_numericas)
    conteos_g = grupo_numerico.count().to_dict()
    conteos_r = resto_numerico.count().to_dict()
    medianas_g = grupo_numerico.median().to_dict()
    medianas_r = resto_numerico.median().to_dict()
    columnas_referencia = [
        columna
        for columna in columnas_numericas
        if columna in referencia_numerica.columns
    ]
    desviaciones = _a_numerico(
        referencia_numerica, columnas_referencia
    ).std(ddof=0).to_dict()
    candidatos: list[tuple[float, int, dict[str, str | float]]] = []

    for orden, columna in enumerate(columnas):
        if columna in {"comedor", "jornada_12h"}:
            resultado_si = _conteo_si(columna, grupo[columna], resto[columna])
            if resultado_si is None:
                continue
            valores, puntuacion = resultado_si
            candidatos.append(
                (puntuacion, orden, {"texto": NOMBRES_CONTEXTO[columna], **valores})
            )
            continue

        n_g = int(conteos_g[columna])
        n_r = int(conteos_r[columna])
        if n_g == 0 or n_r == 0:
            continue

        if columna == "prima_vac_op":
            cuenta_g = int(grupo_numerico[columna].ge(0.5).sum())
            cuenta_r = int(resto_numerico[columna].ge(0.5).sum())
            proporcion_g = cuenta_g / n_g
            proporcion_r = cuenta_r / n_r
            p_comun = (cuenta_g + cuenta_r) / (n_g + n_r)
            error_estandar = sqrt(
                p_comun * (1 - p_comun) * (1 / n_g + 1 / n_r)
            )
            puntuacion = (
                abs(proporcion_g - proporcion_r) / error_estandar
                if error_estandar
                else 0.0
            )
            valores_rasgo: dict[str, str | float] = {
                "texto": NOMBRES_CONTEXTO[columna],
                "grupo": f"{cuenta_g} de {n_g}",
                "resto": f"{cuenta_r} de {n_r}",
            }
        else:
            mediana_g = float(medianas_g[columna])
            mediana_r = float(medianas_r[columna])
            if columna not in referencia_numerica.columns:
                raise ValueError(f"Falta la columna {columna!r} en la referencia.")
            desviacion = float(desviaciones[columna])
            if desviacion == 0 or not pd.notna(desviacion):
                continue
            puntuacion = abs(mediana_g - mediana_r) / desviacion
            valores_rasgo = {
                "texto": NOMBRES_CONTEXTO.get(columna, f"{columna} mediano"),
                "grupo": round(mediana_g, 2),
                "resto": round(mediana_r, 2),
            }
        if puntuacion > 0:
            candidatos.append((puntuacion, orden, valores_rasgo))

    candidatos.sort(key=lambda candidato: (-candidato[0], candidato[1]))
    return [candidato[2] for candidato in candidatos[:n]]
