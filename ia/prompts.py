"""Prompt de sistema y armado del mensaje. Dueño: Julian."""
import json

PROMPT_SISTEMA = """Eres analista senior de compensación. Recibes en JSON una comparación entre la empresa \
del usuario y empresas reales de una encuesta. Escribe máximo tres oraciones en español, \
tono ejecutivo y sin adjetivos de relleno. Explica qué cambió respecto al paso anterior, \
qué significa en pesos y qué más tienen en común las empresas del grupo. Usa solo las \
cifras del JSON. Nunca afirmes que una medida causará un resultado: describe lo que \
muestran las empresas que ya la aplican. Menciona siempre cuántas empresas hay en el grupo.

Reglas de lenguaje:
- Usa "las empresas que ya... muestran", "se observa", "frente a".
- Nunca uses "logrará", "reducirá" ni "si usted hace X, obtendrá Y".
- Usa solo cifras que vengan en el JSON; no las redondees distinto ni inventes ninguna.
- Porcentajes sin decimales (0.222 se escribe 22%) y pesos en millones (6341580 se escribe $6.3 millones).
- Si la señal es "no concluyente" o el grupo se completó con empresas similares, dilo en la tercera oración.
- Responde solo con el texto de la explicación, sin títulos, listas ni comillas."""


def _para_ia(estado):
    """Copia del estado sin lo que la IA no necesita (listas de ids y la explicación vieja)."""
    limpio = {k: v for k, v in estado.items() if k != "explicacion"}
    for parte in ("grupo", "resto"):
        if parte in limpio:
            limpio[parte] = {k: v for k, v in limpio[parte].items() if k != "ids"}
    return limpio


def _json(dato):
    return json.dumps(dato, ensure_ascii=False, indent=2)


def armar_mensaje(estado, anterior):
    """Arma el mensaje para la IA: el cambio, el estado actual y el anterior."""
    cambio = estado.get("cambio")
    partes = [f"Cambio que hizo el usuario:\n{_json(cambio)}" if cambio else "El usuario aún no ha movido ninguna palanca."]
    partes.append(f"Resultado actual:\n{_json(_para_ia(estado))}")
    if anterior:
        partes.append(f"Resultado anterior:\n{_json(_para_ia(anterior))}")
    else:
        partes.append("No hay resultado anterior: es la primera comparación.")
    partes.append("Escribe la explicación.")
    return "\n\n".join(partes)
