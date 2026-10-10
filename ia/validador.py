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

# Números que no vienen del JSON pero que la plantilla usa como texto fijo.
# "100" sale de "rutas a 3 por cada 100 operativos".
NUMEROS_FIJOS = {100.0}

# Llaves del JSON que no son cifras para el usuario:
# - ids: nombres de 40 empresas ("COMPAÑIA 7"); dejarlas permitiría casi cualquier número de 1 a 40.
# - explicacion: es el texto viejo de la IA; no puede validarse a sí mismo.
# - meta: la versión del contrato.
LLAVES_IGNORADAS = {"ids", "explicacion", "meta"}


def _formas(valor):
    """Todas las formas en que una cifra del JSON puede aparecer escrita.

    0.222   -> 0.22, 22.2, 22      (proporción: se escribe como porcentaje)
    6341580 -> 6341580, 6.3        (pesos: se escriben en millones con un decimal)
    323.61  -> 323.61, 324         (salario: con centavos o redondeado)
    """
    v = float(valor)
    formas = {_redondear(v), _redondear(round(v))}
    if abs(v) < 10:  # proporciones (rotación, prima, vales); 10 deja pasar rotaciones de hasta 1000%
        formas |= {_redondear(v * 100), _redondear(round(v * 100)), _redondear(round(v * 100, 1))}
    if abs(v) >= 100_000:  # montos en pesos: "$6.3 millones"
        formas.add(_redondear(round(v / 1_000_000, 1)))
    return formas


def cifras_permitidas(estado):
    """Recorre todo el JSON y junta las formas de cada número que encuentre."""
    permitidas = set(NUMEROS_FIJOS)

    def recorrer(dato):
        if isinstance(dato, bool) or dato is None:  # True es un int en Python: hay que saltarlo antes
            return
        if isinstance(dato, (int, float)):
            permitidas.update(_formas(dato))
        elif isinstance(dato, str):  # "16 de 22" en en_comun, "COMPAÑIA 36" en empresa.id
            for numero in extraer_numeros(dato):
                permitidas.update(_formas(numero))
        elif isinstance(dato, dict):
            for llave, valor in dato.items():
                if llave not in LLAVES_IGNORADAS:
                    recorrer(valor)
        elif isinstance(dato, list):
            for valor in dato:
                recorrer(valor)

    recorrer(estado)
    return permitidas

def es_valido(texto, estado):
    raise NotImplementedError