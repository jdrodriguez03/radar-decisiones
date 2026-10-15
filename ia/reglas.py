"""Reglas de lenguaje de la explicación, revisadas en código. Dueño: Julian.

El validador (ia/validador.py) revisa las CIFRAS; este archivo revisa la FORMA:
- menciona cuántas empresas ya aplican la medida ("22 empresas"),
- no usa palabras que insinúan causa ni palabras prohibidas,
- tiene como máximo 3 oraciones y 75 palabras,
- avisa con palabras sencillas cuando la señal es "no concluyente" o el grupo se completó.

Dos niveles (decisión del día 7):
- fallas_graves(): palabras de causa y advertencia faltante. Las revisa ia/explicar.py EN VIVO:
  si el texto tiene una, se descarta y sale la plantilla, igual que con una cifra inventada.
- revisar(): todas las reglas. Las usan scripts/probar_ia.py y tests/test_reglas_ia.py.
  El largo, la jerga y el n no tumban un texto en vivo: solo sirven para afinar el prompt.
"""
import re

MAX_ORACIONES = 3
MAX_PALABRAS = 75

# Cada palabra se busca como INICIO de palabra y sin importar mayúsculas:
# "reduc" atrapa "reduce", "reducirá" y "reducir".

# Graves: insinúan que la medida CAUSA un resultado. La app solo compara empresas.
CAUSA = [
    "logrará", "lograra", "reduc", "obtendrá", "disminu", "pasaría a",
    "bajará", "mejorará", "evitará", "garantiz", "hará que", "ahorrará",
]

# Solo en pruebas: datos mal dichos, jerga interna y contexto que no está en el JSON.
OTRAS_PROHIBIDAS = [
    "promedio", "dólar", "$0.0",  # son medianas; son pesos; "$0.0 millones" confunde
    "grupo de comparación", "brecha", "rotación", "rotar como",  # jerga del equipo
    "sector", "región",  # el JSON no trae sector ni región
    "así que", "tan pocas", "con solo",  # explican por qué la señal es débil: el aviso ya viene escrito
]

# Alguna de estas debe aparecer si la señal es "no concluyente" o el grupo se completó.
ADVERTENCIAS = ["concluyente", "conclusi", "similares", "cautela", "pocas empresas"]


# Un número o una coma pegados a una letra: "$14.4millones", "millones,porque". La IA a veces se come
# el espacio. La coma de miles ("1,438") no cuenta: después de ella viene un número, no una letra.
NUMERO_PEGADO = re.compile(r"([\d,;])([A-Za-zÁÉÍÓÚÑáéíóúñ])")


def limpiar(texto):
    """Arregla lo que se puede arreglar sin cambiar el sentido: "$14.4millones" -> "$14.4 millones".

    También "millones,porque" -> "millones, porque".

    ia/explicar.py lo aplica antes de validar y mostrar. "lamedida" no se puede arreglar
    en general (habría que saber español): para eso está la temperatura baja.
    """
    return NUMERO_PEGADO.sub(r"\1 \2", texto)


def oraciones(texto):
    """Parte el texto en oraciones.

    Un punto cuenta como fin de oración solo si va seguido de espacio o del final:
    así "$6.3 millones" no se parte en dos. El punto y coma no corta.
    """
    partes = re.split(r"(?<=[.!?])\s+", texto.strip())
    return [p for p in partes if p]


def _usa(texto, palabra):
    """True si `palabra` aparece al inicio de una palabra del texto, sin importar mayúsculas."""
    return re.search(r"(?<!\w)" + re.escape(palabra), texto, flags=re.IGNORECASE) is not None


def menciona_n(texto, n):
    """True si el texto dice "N empresas" ("Las 22 empresas", "quedan 16 empresas").

    No basta con que el número aparezca: en el guion el grupo es de 22 empresas y pierden 22%,
    así que un texto sin "22 empresas" pasaría por el 22%. También acepta la forma de
    derivadas: "22 de las 38 empresas".
    """
    patron = rf"(?<![\d.,]){int(n)}(?:\s+de\s+las\s+\d+)?\s+empresas"
    return re.search(patron, texto, flags=re.IGNORECASE) is not None


def necesita_advertencia(estado):
    grupo = estado.get("grupo") or {}
    return (estado.get("senal") or {}).get("etiqueta") == "no concluyente" or bool(grupo.get("completado"))


def fallas_graves(texto, estado):
    """Lo que nunca puede llegar a la pantalla: palabras de causa y advertencia faltante."""
    fallas = [f"usa «{palabra}»" for palabra in CAUSA if _usa(texto, palabra)]
    if necesita_advertencia(estado) and not any(_usa(texto, a) for a in ADVERTENCIAS):
        fallas.append("no advierte que la señal no es concluyente o que el grupo se completó")
    return fallas


def revisar(texto, estado):
    """Todas las reglas que el texto NO cumple. Lista vacía = el texto está bien."""
    fallas = fallas_graves(texto, estado)
    n = (estado.get("grupo") or {}).get("n")
    if estado.get("cambio") and n is not None and not menciona_n(texto, n):
        fallas.append(f"no menciona las {n} empresas del grupo")
    fallas += [f"usa «{palabra}»" for palabra in OTRAS_PROHIBIDAS if _usa(texto, palabra)]
    total = len(oraciones(texto))
    if total > MAX_ORACIONES:
        fallas.append(f"tiene {total} oraciones (máximo {MAX_ORACIONES})")
    if NUMERO_PEGADO.search(texto):
        fallas.append("tiene un número pegado a una palabra")
    palabras = len(texto.split())
    if palabras > MAX_PALABRAS:
        fallas.append(f"tiene {palabras} palabras (máximo {MAX_PALABRAS})")
    return fallas
