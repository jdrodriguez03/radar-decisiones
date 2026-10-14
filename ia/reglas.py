"""Reglas de lenguaje de la explicación, revisadas en código. Dueño: Julian.

El validador (ia/validador.py) revisa las CIFRAS; este archivo revisa la FORMA:
- menciona cuántas empresas ya aplican la medida (el n del grupo),
- no usa palabras que insinúan causa ("logrará", "reducirá"...) ni palabras prohibidas,
- tiene como máximo 3 oraciones y MAX_PALABRAS palabras,
- avisa con palabras sencillas cuando la señal es "no concluyente" o el grupo se completó.

Lo usan scripts/probar_ia.py (para revisar los 15 textos) y tests/test_reglas_ia.py.
"""
import re

from ia.validador import extraer_numeros

MAX_ORACIONES = 3
MAX_PALABRAS = 75

# Palabras que el texto nunca puede usar. Se buscan como inicio de palabra:
# "reduc" atrapa "reduce", "reducirá" y "reducir"; "sector" atrapa "sectores".
PROHIBIDAS = [
    "logrará", "lograra", "reduc", "obtendrá", "disminu", "pasaría a",  # causa
    "promedio",  # son medianas
    "grupo de comparación", "brecha", "rotación", "rotar como",  # jerga
    "sector", "región", "dólar",  # fuera del JSON
    "$0.0",
]

# Alguna de estas debe aparecer si la señal es "no concluyente" o el grupo se completó.
ADVERTENCIAS = ["concluyente", "conclusi", "similares", "cautela", "pocas empresas"]


def oraciones(texto):
    """Parte el texto en oraciones.

    Un punto cuenta como fin de oración solo si va seguido de espacio o del final:
    así "$6.3 millones" no se parte en dos.
    """
    partes = re.split(r"(?<=[.!?])\s+", texto.strip())
    return [p for p in partes if p]


def _usa(texto, palabra):
    """True si `palabra` aparece al inicio de una palabra del texto, sin importar mayúsculas."""
    return re.search(r"(?<!\w)" + re.escape(palabra), texto, flags=re.IGNORECASE) is not None


def necesita_advertencia(estado):
    grupo = estado.get("grupo") or {}
    return (estado.get("senal") or {}).get("etiqueta") == "no concluyente" or bool(grupo.get("completado"))


def revisar(texto, estado):
    """Lista de reglas que el texto NO cumple. Lista vacía = el texto está bien."""
    fallas = []
    n = (estado.get("grupo") or {}).get("n")
    if estado.get("cambio") and n is not None and float(n) not in extraer_numeros(texto):
        fallas.append(f"no menciona las {n} empresas del grupo")
    for palabra in PROHIBIDAS:
        if _usa(texto, palabra):
            fallas.append(f"usa «{palabra}»")
    total = len(oraciones(texto))
    if total > MAX_ORACIONES:
        fallas.append(f"tiene {total} oraciones (máximo {MAX_ORACIONES})")
    palabras = len(texto.split())
    if palabras > MAX_PALABRAS:
        fallas.append(f"tiene {palabras} palabras (máximo {MAX_PALABRAS})")
    if necesita_advertencia(estado) and not any(_usa(texto, a) for a in ADVERTENCIAS):
        fallas.append("no advierte que la señal no es concluyente o que el grupo se completó")
    return fallas
