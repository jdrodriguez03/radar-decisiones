"""API que reúne el estado calculado por el motor para la interfaz."""

import hashlib
import json
from collections import OrderedDict
from copy import deepcopy
from threading import RLock
from weakref import ReferenceType, ref

import pandas as pd

from config import PALANCAS
from contrato.modelo import validar
from motor.comparar import INDICADORES, comparar
from motor.en_comun import diferencias_principales
from motor.pesos import costo_brecha, costo_medida

_MAX_ESTADOS_CACHE = 128
_ESTADOS_CACHE: OrderedDict[str, dict] = OrderedDict()
_ESTADOS_CACHE_LOCK = RLock()
_HUELLAS_DATAFRAME: dict[
    int, tuple[ReferenceType[pd.DataFrame], pd.DataFrame, str]
] = {}


def _columnas_resultado(empresas):
    columnas_resultado = {
        "empresa",
        "banda",
        "comedor",
        "jornada_12h",
        "fondo_op",
        *PALANCAS,
        *INDICADORES.values(),
    }
    return [
        columna
        for columna in empresas.columns
        if columna in columnas_resultado
        or (isinstance(columna, str) and columna.startswith("m_"))
    ]


def _banda_por_plantilla(plantilla):
    if plantilla <= 186:
        return "chica"
    if 202 <= plantilla <= 570:
        return "mediana"
    if plantilla >= 627:
        return "grande"
    return None


def _empresas_con_perfil(empresas, perfil):
    """Añade un perfil externo como fila-ancla para excluirlo del universo."""
    if "empresa" not in empresas.columns or perfil["id"] in empresas["empresa"].to_numpy():
        return empresas

    fila = {
        "empresa": perfil["id"],
        "plantilla_op": perfil["plantilla_op"],
        "rot_anual": perfil["indicadores"]["rot_anual"],
        "bajas_menos3m": perfil["indicadores"].get("rot_temprana"),
        "aus_inj_op": perfil["indicadores"].get("ausentismo"),
    }
    fila.update({columna: perfil["palancas"].get(columna) for columna in PALANCAS})
    if "banda" in empresas.columns:
        fila["banda"] = _banda_por_plantilla(perfil["plantilla_op"])
    return pd.concat([empresas, pd.DataFrame([fila])], ignore_index=True)


def _clave_cache(empresas, perfil, palancas_movidas, cambio, supuestos, solo_tamano):
    huella_datos = _huella_dataframe(empresas)
    entradas = json.dumps(
        [perfil, palancas_movidas, cambio, supuestos, solo_tamano],
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return f"{huella_datos}:{entradas}"


def _huella_dataframe(empresas):
    """Reutiliza el hash mientras una instantánea confirma que el DataFrame no cambió."""
    identidad = id(empresas)
    with _ESTADOS_CACHE_LOCK:
        almacenada = _HUELLAS_DATAFRAME.get(identidad)
        if almacenada is not None:
            referencia, instantanea, huella = almacenada
            if referencia() is empresas and empresas.equals(instantanea):
                return huella

        datos_huella = empresas[_columnas_resultado(empresas)]
        hash_filas = pd.util.hash_pandas_object(
            datos_huella, index=True
        ).values.tobytes()
        huella = hashlib.blake2b(
            repr((tuple(empresas.columns), tuple(map(str, empresas.dtypes)))).encode()
            + hash_filas,
            digest_size=16,
        ).hexdigest()

        def eliminar(referencia, identidad=identidad):
            with _ESTADOS_CACHE_LOCK:
                actual = _HUELLAS_DATAFRAME.get(identidad)
                if actual is not None and actual[0] is referencia:
                    del _HUELLAS_DATAFRAME[identidad]

        _HUELLAS_DATAFRAME[identidad] = (
            ref(empresas, eliminar),
            empresas.copy(deep=True),
            huella,
        )
        return huella


# Función principal de la API que calcula y valida el estado completo de una empresa y sus comparables.
def calcular_estado(empresas, perfil, palancas_movidas, cambio, supuestos, solo_tamano=False):
    """Calcula y valida el estado completo de una empresa y sus comparables.

    Si el perfil no existe en la base, se añade solo como ancla para aplicar los
    filtros; no forma parte del grupo ni del resto. Los resultados se guardan
    temporalmente en caché por datos y entradas, devolviendo copias independientes.
    """
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

    clave = _clave_cache(
        empresas, perfil, palancas_movidas, cambio, supuestos, solo_tamano
    )
    with _ESTADOS_CACHE_LOCK:
        if clave in _ESTADOS_CACHE:
            _ESTADOS_CACHE.move_to_end(clave)
            return deepcopy(_ESTADOS_CACHE[clave])

    empresas_analisis = _empresas_con_perfil(
        empresas[_columnas_resultado(empresas)], perfil
    )
    comparacion = comparar(
        empresas_analisis,
        perfil["id"],
        palancas_movidas,
        solo_tamano=solo_tamano,
    )
    grupo_ids = comparacion["grupo"]["ids"]
    resto_ids = comparacion["resto"]["ids"]
    columnas_rasgos = [
        *PALANCAS,
        "comedor",
        "jornada_12h",
        "fondo_op",
        *sorted(
            columna
            for columna in empresas_analisis.columns
            if columna.startswith("m_")
        ),
    ]
    columnas_rasgos = [
        "empresa",
        *dict.fromkeys(
            columna for columna in columnas_rasgos if columna in empresas_analisis
        ),
    ]
    por_id = empresas_analisis[columnas_rasgos].set_index("empresa", drop=False)
    grupo = por_id.loc[grupo_ids].reset_index(drop=True)
    resto = por_id.loc[resto_ids].reset_index(drop=True)
    rasgos = diferencias_principales(
        grupo,
        resto,
        palancas_movidas=palancas_movidas,
        referencia=empresas,
    )
    resumen_grupo = {
        **comparacion["grupo"],
        "completado": comparacion["completado"],
    }
    rot_grupo = resumen_grupo["indicadores"]["rot_anual"]
    if rot_grupo is None:
        raise ValueError(
            "No se puede calcular el costo de brecha: el grupo no tiene rotación anual."
        )
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
    resultado = validar(estado).model_dump(mode="json")
    with _ESTADOS_CACHE_LOCK:
        _ESTADOS_CACHE[clave] = deepcopy(resultado)
        _ESTADOS_CACHE.move_to_end(clave)
        while len(_ESTADOS_CACHE) > _MAX_ESTADOS_CACHE:
            _ESTADOS_CACHE.popitem(last=False)
    return resultado
