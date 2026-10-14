"""Revisa que toda cifra del texto exista en el JSON. Dueño: Julian."""
import math
import re

from ia.derivadas import cifras_derivadas

# Un número tal como lo escribe la IA: "1,438" (miles con coma), "6.3" (decimal) o "22" (entero).
# La alternativa de miles va primero: si no, "1,438" saldría como 1 y 438.
PATRON_NUMERO = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")


def _redondear(x):
    """Todas las cifras se comparan con 2 decimales, para que 22 y 22.0 sean lo mismo."""
    return round(float(x), 2)


def extraer_numeros(texto):
    """'pierden 22% ... $6.3 millones ... 1,438' -> [22.0, 6.3, 1438.0]"""
    return [_redondear(n.replace(",", "")) for n in PATRON_NUMERO.findall(texto)]


# Números del idioma, no de los datos: el texto puede usarlos aunque no estén en el JSON.
# - 100: "de cada 100 operativos" y "rutas por cada 100 operativos".
# - 3:   "se van antes de 3 meses" (así se define la rotación temprana).
# - 12:  "los 12 meses del año".
# Cada número que se agrega aquí abre un hueco (un 12% inventado pasaría). Por eso son pocos.
NUMEROS_FIJOS = {100.0, 3.0, 12.0}

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
        porcentaje = round(v * 100, 6)  # 0.29 * 100 da 28.999999999999996: se limpia antes de redondear
        formas |= {
            _redondear(porcentaje),
            _redondear(round(porcentaje)),  # 0.516 -> 52 (al más cercano)
            _redondear(math.floor(porcentaje)),  # 0.516 -> 51 (hacia abajo): un punto de redondeo no es un invento
            _redondear(round(porcentaje, 1)),
        }
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
    # Las métricas precalculadas (ia/derivadas.py) ya vienen en su forma final (58, 1.4, 742):
    # se agregan exactas, sin _formas, para no abrir huecos como 140 o 1 a partir de 1.4.
    for derivada in cifras_derivadas(estado).values():
        permitidas.add(_redondear(derivada["valor"]))
    return permitidas


def cifras_inventadas(texto, estado, anterior=None):
    """Lista de los números del texto que no salen del estado ni del paso anterior.

    Sirve para depurar: en el sandbox se puede mostrar cuál cifra falló.
    """
    permitidas = cifras_permitidas(estado)
    if anterior:  # "quedan 16 empresas, antes 22": el 22 viene del paso anterior
        permitidas |= cifras_permitidas(anterior)
    return [n for n in extraer_numeros(texto) if n not in permitidas]


def es_valido(texto, estado, anterior=None):
    """True si todas las cifras del texto existen en el estado (o en el anterior)."""
    return not cifras_inventadas(texto, estado, anterior)