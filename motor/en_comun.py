"""Diferencias principales entre grupo y resto. Dueño: Aleja."""
from __future__ import annotations

from math import sqrt
from numbers import Integral

import pandas as pd

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
    validos = pd.concat([grupo.dropna(), resto.dropna()])
    if validos.empty:
        return None
    normalizados = validos.map(
        lambda valor: str(valor).strip().casefold().replace("í", "i")
    )
    permitidos = {"si", "no", "yes", "true", "false"}
    inesperados = set(normalizados).difference(permitidos)
    if inesperados:
        raise ValueError(
            f"Valores no reconocidos en la columna Sí/No {columna}: {sorted(inesperados)}"
        )

    g_validos = grupo.dropna()
    r_validos = resto.dropna()
    cuenta_g = int(g_validos.map(_es_si).sum())
    cuenta_r = int(r_validos.map(_es_si).sum())
    proporcion_g = cuenta_g / len(g_validos) if len(g_validos) else 0.0
    proporcion_r = cuenta_r / len(r_validos) if len(r_validos) else 0.0

    p_comun = (cuenta_g + cuenta_r) / (len(g_validos) + len(r_validos))
    error_estandar = sqrt(
        p_comun * (1 - p_comun) * (1 / len(g_validos) + 1 / len(r_validos))
    ) if len(g_validos) and len(r_validos) else 0.0
    puntuacion = abs(proporcion_g - proporcion_r) / error_estandar if error_estandar else 0.0
    return (
        {
            "grupo": f"{cuenta_g} de {len(g_validos)}",
            "resto": f"{cuenta_r} de {len(r_validos)}",
        },
        puntuacion,
    )

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

        grupo_numerico = pd.to_numeric(grupo[columna], errors="coerce")
        resto_numerico = pd.to_numeric(resto[columna], errors="coerce")
        validos_g = grupo_numerico.dropna()
        validos_r = resto_numerico.dropna()
        if validos_g.empty or validos_r.empty:
            continue

        if columna == "prima_vac_op":
            cuenta_g = int(validos_g.ge(0.5).sum())
            cuenta_r = int(validos_r.ge(0.5).sum())
            proporcion_g = cuenta_g / len(validos_g)
            proporcion_r = cuenta_r / len(validos_r)
            p_comun = (cuenta_g + cuenta_r) / (len(validos_g) + len(validos_r))
            error_estandar = sqrt(
                p_comun * (1 - p_comun) * (1 / len(validos_g) + 1 / len(validos_r))
            )
            puntuacion = (
                abs(proporcion_g - proporcion_r) / error_estandar
                if error_estandar
                else 0.0
            )
            valores_rasgo: dict[str, str | float] = {
                "texto": NOMBRES_CONTEXTO[columna],
                "grupo": f"{cuenta_g} de {len(validos_g)}",
                "resto": f"{cuenta_r} de {len(validos_r)}",
            }
        else:
            mediana_g = float(validos_g.median())
            mediana_r = float(validos_r.median())
            if columna not in referencia_numerica.columns:
                raise ValueError(f"Falta la columna {columna!r} en la referencia.")
            valores_referencia = pd.to_numeric(
                referencia_numerica[columna], errors="coerce"
            ).dropna()
            desviacion = float(valores_referencia.std(ddof=0))
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
