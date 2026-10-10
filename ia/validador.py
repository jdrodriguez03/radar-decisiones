"""Revisa que toda cifra del texto exista en el JSON. Dueño: Julian."""
import re

# Un número tal como lo escribe la IA: "1,438" (miles con coma), "6.3" (decimal) o "22" (entero).
# La alternativa de miles va primero: si no, "1,438" saldría como 1 y 438.
PATRON_NUMERO = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")


def _redondear(x):
    """Todas las cifras se comparan con 2 decimales, para que 22 y 22.0 sean lo mismo."""
    return round(float(x), 2)


def extraer_numeros(texto):
    """'pierden 22% ... $6.3 millones ... 1,438' -> [22.0, 6.3, 1438.0]"""
    return [_redondear(n.replace(",", "")) for n in PATRON_NUMERO.findall(texto)]


def es_valido(texto, estado):
    raise NotImplementedError