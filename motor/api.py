"""API que reúne el estado calculado por el motor para la interfaz."""

import pandas as pd

from contrato.modelo import validar
from motor.comparar import comparar
from motor.en_comun import diferencias_principales
from motor.pesos import costo_brecha, costo_medida


# Función principal de la API que calcula y valida el estado completo de una empresa y sus comparables.
def calcular_estado(empresas, perfil, palancas_movidas, cambio, supuestos, solo_tamano=False):
    """Calcula y valida el estado completo de una empresa y sus comparables."""
    if not isinstance(empresas, pd.DataFrame):
        raise TypeError("empresas debe ser un DataFrame.")
    if not isinstance(perfil, dict) or not isinstance(perfil.get("id"), str):
        raise TypeError("perfil debe ser un diccionario con id de empresa.")
    if not isinstance(perfil.get("palancas"), dict):
        raise TypeError("perfil debe incluir palancas como diccionario.")
    if not isinstance(perfil.get("indicadores"), dict):
        raise TypeError("perfil debe incluir indicadores como diccionario.")
    if not isinstance(palancas_movidas, dict):
        raise TypeError("palancas_movidas debe ser un diccionario.")
    if not isinstance(supuestos, dict) or "costo_por_baja" not in supuestos:
        raise ValueError("supuestos debe incluir costo_por_baja.")
    if "costo_ruta_mensual" not in supuestos:
        raise ValueError("supuestos debe incluir costo_ruta_mensual.")

    comparacion = comparar(
        empresas,
        perfil["id"],
        palancas_movidas,
        solo_tamano=solo_tamano,
    )
    grupo_ids = comparacion["grupo"]["ids"]
    resto_ids = comparacion["resto"]["ids"]
    por_id = empresas.set_index("empresa", drop=False)
    grupo = por_id.loc[grupo_ids].reset_index(drop=True)
    resto = por_id.loc[resto_ids].reset_index(drop=True)
# Se calculan las diferencias principales entre el grupo y el resto, excluyendo las palancas movidas y utilizando el conjunto de empresas como referencia para calcular desviaciones estándar.
    rasgos = diferencias_principales(
        grupo,
        resto,
        palancas_movidas=palancas_movidas,
        referencia=empresas,
    )
# Se crea un resumen del grupo que incluye el número de empresas, los indicadores y si se completó la comparación.
    resumen_grupo = {
        **comparacion["grupo"],
        "completado": comparacion["completado"],
    }
    rot_grupo = resumen_grupo["indicadores"]["rot_anual"]
    if rot_grupo is None:
        raise ValueError("No se puede calcular el costo de brecha: el grupo no tiene rotación anual.")
# Se construye el estado final que incluye la versión, la empresa, el cambio, las palancas movidas, el grupo, el resto, la señal, los rasgos y los pesos calculados.
    estado = {
        "meta": {"version": 1},
        "empresa": perfil,
        "cambio": cambio,
        "palancas_movidas": palancas_movidas,
        "grupo": resumen_grupo,
        "resto": comparacion["resto"],
        "senal": comparacion["senal"],
        "en_comun": rasgos,
        "pesos": {
            "costo_medida_anual": costo_medida(perfil, palancas_movidas, supuestos),
            "costo_brecha_anual": costo_brecha(
                perfil["indicadores"]["rot_anual"],
                rot_grupo,
                perfil["plantilla_op"],
                supuestos["costo_por_baja"],
            ),
            "supuestos": supuestos,
        },
    }
    return validar(estado).model_dump(mode="json")
