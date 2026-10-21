"""Semáforo de evidencia: hacia dónde va la comparación y qué tan sólida es. Dueño: Julian.

Decisión de Julian (17 de octubre): reemplaza a la pregunta libre como extra del bloque 5.

Responde dos preguntas por separado, en dos apartados:
1. Dirección: ¿las empresas que ya aplican la medida rotan menos o más que las demás?
   Se compara la rotación anual (mediana) del grupo contra la del resto.
2. Solidez: ¿esa diferencia es real o pudo ser casualidad? Es la señal estadística que ya
   calcula el motor (Mann-Whitney): clara, débil o no concluyente.

Qué NO dice: que la medida funcione ni que la decisión sea buena. Solo describe lo que
muestran las empresas que ya lo hacen ("rotan menos", nunca "hace que roten menos").
Todo sale de cifras que ya vienen en el contrato: no hay umbrales nuevos ni fórmulas inventadas.
"""

# De menos a más sólida. El número es la posición en la barra (1 = izquierda, 3 = derecha).
NIVELES = {
    "naranja": 1,
    "amarillo": 2,
    "verde": 3,
}


def _dato(estado, *ruta):
    """Busca un valor siguiendo la ruta de llaves; None si falta alguna."""
    for clave in ruta:
        if not isinstance(estado, dict):
            return None
        estado = estado.get(clave)
    return estado


def _hay_comparacion(estado):
    """False en el estado inicial (sin palancas movidas) o si falta la rotación de un lado."""
    return bool(
        estado.get("cambio")
        and estado.get("palancas_movidas")
        and _dato(estado, "grupo", "indicadores", "rot_anual") is not None
        and _dato(estado, "resto", "indicadores", "rot_anual") is not None
    )


def _millones(pesos):
    return f"${abs(pesos) / 1_000_000:.1f} M"


def direccion(estado):
    """Apartado 1: ¿las empresas que lo hacen rotan menos o más? None si no hay comparación.

    Devuelve {"rotan_mas", "titulo", "detalle"}. "Rotan más" incluye el empate: si rotan igual,
    las empresas que lo hacen no muestran nada a favor, y eso también es una alerta.
    """
    if not _hay_comparacion(estado):
        return None
    rot_grupo = _dato(estado, "grupo", "indicadores", "rot_anual")
    rot_resto = _dato(estado, "resto", "indicadores", "rot_anual")
    n = _dato(estado, "grupo", "n")
    rotan_mas = rot_grupo >= rot_resto
    return {
        "rotan_mas": rotan_mas,
        "titulo": "⚠ Rotan más" if rotan_mas else "↓ Rotan menos",
        "detalle": f"{n} empresas que lo hacen: {rot_grupo:.0%} al año contra {rot_resto:.0%} de las que no",
    }


def solidez(estado):
    """Apartado 2: ¿la diferencia es real o pudo ser casualidad? None si no hay comparación.

    Verde = señal clara, amarillo = señal débil, naranja = no concluyente. Si las empresas que lo
    hacen rotan más, la etiqueta agrega "de que rotan más" (salvo en naranja, que no afirma nada).
    Si el grupo se completó con empresas similares, también es naranja: ya no son empresas
    que de verdad aplican la medida. Devuelve {"color", "nivel", "etiqueta"}.
    """
    if not _hay_comparacion(estado):
        return None
    senal = _dato(estado, "senal", "etiqueta")
    completado = bool(_dato(estado, "grupo", "completado"))
    if senal in (None, "no aplica"):
        return None
    if senal == "clara" and not completado:
        color, etiqueta = "verde", "Evidencia clara"
    elif senal == "débil" and not completado:
        color, etiqueta = "amarillo", "Evidencia débil"
    else:
        color, etiqueta = "naranja", "No concluyente"
    # Si las empresas que lo hacen rotan más, la etiqueta lo dice: un verde solo ("Evidencia clara")
    # bajo la alerta roja podría leerse como "bueno", cuando significa "es claro que rotan más".
    rotan_mas = _dato(estado, "grupo", "indicadores", "rot_anual") >= _dato(estado, "resto", "indicadores", "rot_anual")
    if rotan_mas and color != "naranja":
        etiqueta += " de que rotan más"
    if completado:
        etiqueta += " · completado con similares"
    return {"color": color, "nivel": NIVELES[color], "etiqueta": etiqueta}


def lectura_pesos(estado):
    """Una frase que pone lado a lado lo que cuesta la medida y lo que cuesta la diferencia en bajas.

    No divide una cifra entre la otra (eso insinúa un retorno, y el proyecto lo prohíbe):
    solo dice cuál es mayor. None si no aplica (estado inicial o sin pesos).
    """
    if not estado.get("cambio"):
        return None
    medida = _dato(estado, "pesos", "costo_medida_anual")
    brecha = _dato(estado, "pesos", "costo_brecha_anual")
    if medida is None or brecha is None:
        return None
    if brecha == 0:
        return "Su empresa ya rota menos que esas empresas"
    if medida < 0:
        return f"La medida ahorra {_millones(medida)} al año; la diferencia en bajas es de {_millones(brecha)}"
    if medida < brecha:
        return f"La medida ({_millones(medida)}) cuesta menos que la diferencia en bajas ({_millones(brecha)})"
    return f"La medida ({_millones(medida)}) cuesta más que la diferencia en bajas ({_millones(brecha)})"
