"""Prompt de sistema y armado del mensaje. Dueño: Julian."""
import json
import re

from config import MIN_GRUPO
from ia.derivadas import cifras_derivadas
from ia.reglas import necesita_advertencia

PROMPT_SISTEMA = """Eres analista senior de compensación. Recibes en JSON una comparación entre la empresa \
del usuario y empresas reales de una encuesta. Escribe exactamente tres oraciones en español, \
máximo 75 palabras en total, con tono ejecutivo y palabras sencillas, para un directivo que no es analista. \
Usa solo las cifras del JSON y pocas: las que pide cada oración, ninguna más. \
Nunca afirmes que una medida causará un resultado: describe lo que muestran las empresas que ya la aplican.

Estructura, una oración por punto:
1. La comparación: cuántas empresas ya aplican todo lo que el usuario movió y cuánto de su plantilla pierden al año, frente a cuánto pierden las demás. \
Nombra en español natural (aguinaldo, prima vacacional, salario inicial, vales, rutas) cada palanca de "palancas_movidas" con su nivel, no solo la última: esas empresas cumplen todas a la vez. \
Si el mensaje trae "Qué cambió frente al paso anterior", empieza con las palancas de "Cambios desde la última explicación" (nuevas o cambiadas), \
después las que "Ya tenía", y di cuántas empresas quedan frente a cuántas había \
(por ejemplo, "Con la prima vacacional de 50% y el salario inicial de $350, sumados al aguinaldo de 20 días, quedan 5 empresas, antes 22"); \
si quitó una palanca, dilo en pocas palabras ("sin la prima vacacional"). Nombra cada palanca solo con su nivel nuevo: \
nunca escribas su valor anterior ("de 25% a 50%"), que ya se ve en pantalla. Del paso anterior usa solo cifras que aparezcan en esa lista.
2. Qué significa en pesos para su empresa: esa diferencia en bajas por año frente al costo anual de la medida. \
Si el JSON trae "nota_pesos", esta oración dice eso con el porcentaje que pierde hoy su empresa, sin comparar costos ni escribir "$0".
3. Algo más que tienen en común esas mismas empresas frente a las demás, sin cifras. \
Usa el único elemento de "en_comun": nombra el rasgo en palabras con su "como_decirlo" tal cual \
(por ejemplo, "la mayoría de esas empresas también da prima vacacional de 50% o más" o "esas empresas suelen tener un salario inicial más alto"); \
nunca digas "todas" si "como_decirlo" no dice "todas". Si "en_comun" viene vacío, no menciones ningún rasgo. \
Si el JSON trae "aviso", esta oración es ese aviso, copiado tal cual y sin agregar nada más. \
Si el usuario aún no ha movido ninguna palanca, esta oración lo invita a mover una para ver qué muestran las empresas que ya la aplican.

Si el usuario aún no ha movido ninguna palanca, la oración 2 no habla de pesos: dice el tamaño del problema en personas, \
con "personas_que_pierde_al_año" y "personas_que_se_van_antes_de_3_meses" de "derivadas" \
(por ejemplo, "Eso son unas 742 personas al año, y unas 297 se van antes de cumplir 3 meses").

Forma de la explicación (lo que va entre llaves se llena con datos del JSON):
"Las {n} empresas que ya {dan o tienen} {palanca y nivel} o más pierden {X}% de su plantilla al año; las demás, {Y}%. Para su empresa, esa diferencia equivale a ${A} millones de pesos al año en bajas, contra ${B} millones de pesos que costaría la medida. Además, {la mayoría} de esas empresas {característica en palabras}."

Forma cuando hay paso anterior (más corta: no repitas el número de empresas en la misma oración):
"Con {palancas nuevas y su nivel}, sumadas a {las que ya tenía y su nivel}, quedan {n} empresas, antes {n anterior}; pierden {X}% de su plantilla al año y las demás, {Y}%. Para su empresa, la diferencia equivale a ${A} millones de pesos al año en bajas, contra ${B} millones de la medida. Además, esas empresas {rasgo con su como_decirlo}."

Reglas de lenguaje:
- Usa "las empresas que ya... muestran", "se observa", "frente a" cuando ayuden a la claridad.
- Nunca digas que una medida causa algo: no uses "logrará", "reducirá", "reduce", "disminuye", "pasaría a" ni "si usted hace X, obtendrá Y".
- No menciones sectores, regiones ni nada que no esté en el JSON.
- No uses las palabras "grupo de comparación", "brecha", "rotar como ese grupo" ni "rotación"; di "pierden X% de su plantilla al año".
- Usa solo cifras que vengan en el JSON; no inventes ninguna. No hagas cuentas propias (restas, divisiones, \
conversiones a personas o a porcentajes): las únicas cifras calculadas permitidas están en "derivadas", y se escriben con su valor tal cual.
- Cómo usar "derivadas", como máximo una por oración y sin pasar de 75 palabras: \
en la oración 1 puedes decir qué tan común es la medida ("22 de las 38 empresas comparables, 58%, ya lo hacen"); \
en la oración 2 puedes decir el costo como porcentaje de la nómina operativa base o la diferencia en personas al año.
- Las proporciones sencillas dilas con palabras ("la mitad", "la mayoría", "casi todas"); no escribas "1 de cada 2".
- No expliques por qué la señal es clara, débil o no concluyente (no digas "así que" ni "con tan pocas empresas"): solo di cuál es.
- Porcentajes al entero más cercano (0.516 es 52%, no 51%); los valores como 0.25 de prima o de vales se escriben como porcentaje (25%). Pesos en millones con un decimal (6341580 es $6.3 millones de pesos); \
los montos de menos de un millón, en miles sin decimales (250079 es $250 mil pesos).
- Si el JSON trae "nota_resto", las demás empresas son muy pocas: escribe "las otras N empresas" con su número en lugar de "las demás".
- Deja siempre un espacio entre un número y la palabra que le sigue ("$14.4 millones", no "$14.4millones").
- Todos los montos están en pesos mexicanos: nunca los llames dólares ni los conviertas a otra moneda.
- Si la diferencia en pesos es 0 (su empresa ya pierde igual o menos gente que esas empresas), dilo así en la segunda oración, sin comparar costos.
- Responde solo con el texto de la explicación, sin títulos, listas ni comillas.
- Las cifras de las empresas son medianas: nunca digas "promedio"; si hace falta, di "a la mitad de la tabla" o no lo califiques."""


def como_decirlo(rasgo):
    """Decide en código cómo nombrar un rasgo de en_comun, para que la IA no lo adivine.

    Conteo como "16 de 22"  -> "la mayoría" (según la proporción).
    Dos números (medianas)  -> "suelen tener un valor más alto/más bajo que las demás".
    """
    grupo, resto = rasgo.get("grupo"), rasgo.get("resto")
    if isinstance(grupo, str) and " de " in grupo:
        tienen, total = (int(x) for x in grupo.split(" de "))
        proporcion = tienen / total if total else 0
        if proporcion == 1:
            return "todas"
        if proporcion == 0:
            return "ninguna"
        if proporcion >= 0.8:
            return "casi todas"
        if proporcion > 0.5:
            return "la mayoría"
        if proporcion >= 0.25:
            return "algunas"
        return "pocas"
    if isinstance(grupo, (int, float)) and isinstance(resto, (int, float)):
        if abs(grupo - resto) <= 0.03 * max(abs(grupo), abs(resto)):  # menos de 3% de diferencia
            return "tienen un valor parecido al de las demás"
        return f"suelen tener un valor más {'alto' if grupo > resto else 'bajo'} que las demás"
    return "algunas"


# Cómo aparece cada palanca en el texto de los rasgos de en_comun
NOMBRES_PALANCA = {
    "sal_dia_ini": "salario inicial",
    "aguinaldo_op": "aguinaldo",
    "prima_vac_op": "prima vacacional",
    "vales_op": "vales",
    "rutas_x100": "rutas",
}


def rasgos_utiles(estado):
    """Rasgos de en_comun que dicen algo nuevo.

    Quita los de palancas que el usuario movió: esas empresas se eligieron justo por
    tenerlas, así que decir "todas dan prima de 50%" no aporta nada.
    """
    movidas = [NOMBRES_PALANCA[p] for p in (estado.get("palancas_movidas") or {}) if p in NOMBRES_PALANCA]
    return [r for r in estado.get("en_comun") or [] if not any(m in r.get("texto", "") for m in movidas)]


AVISO_COMPLETADO = (
    "Como hay pocas empresas con esta combinación, se sumaron otras similares: tómelo como referencia, no como conclusión."
)
AVISO_NO_CONCLUYENTE = "Con estos datos la señal no es concluyente: tómelo como referencia, no como conclusión."


def aviso_senal(estado):
    """La frase de advertencia ya escrita, o None si no hace falta.

    Se le da hecha a la IA (como nota_pesos): cuando la inventaba, explicaba por qué
    ("con solo 20 empresas") o la unía al rasgo con "así que", que no tiene lógica.
    """
    if (_dato(estado, ("grupo", "completado"))):
        return AVISO_COMPLETADO
    if necesita_advertencia(estado):
        return AVISO_NO_CONCLUYENTE
    return None


def nombre_rasgo(texto):
    """'fondo de ahorro mediano' -> 'fondo de ahorro': "mediano" es jerga del motor, no del directivo."""
    return re.sub(r"\s+median[oa]s?\b", "", texto).strip()


def _para_ia(estado):
    """Copia del estado sin lo que la IA no necesita (ids, la explicación vieja y el último clic).

    De en_comun deja solo el primer rasgo útil, con su "como_decirlo" calculado aquí.
    """
    # "cambio" es solo el último clic: con el botón Explicar puede haber varios cambios,
    # y esos ya van en palabras arriba del JSON (describir_cambios). Mandar los dos confunde.
    limpio = {k: v for k, v in estado.items() if k not in ("explicacion", "cambio")}
    for parte in ("grupo", "resto"):
        if parte in limpio:
            limpio[parte] = {k: v for k, v in limpio[parte].items() if k != "ids"}
    if "en_comun" in limpio:
        # Con aviso no se manda el rasgo: la IA juntaba los dos ("no es concluyente, así que esas
        # empresas...") y pasaba de 75 palabras. Lo que no recibe, no lo puede usar.
        rasgos = [] if necesita_advertencia(estado) else rasgos_utiles(estado)[:1]
        limpio["en_comun"] = [
            {**rasgo, "texto": nombre_rasgo(rasgo.get("texto", "")), "como_decirlo": como_decirlo(rasgo)} for rasgo in rasgos
        ]
    aviso = aviso_senal(estado)
    if aviso:
        limpio["aviso"] = aviso
    n_resto = _dato(estado, ("resto", "n"))
    if estado.get("palancas_movidas") and n_resto is not None and 0 < n_resto < MIN_GRUPO:
        limpio["nota_resto"] = f"Las demás son solo {n_resto} empresas: escribe \"las otras {n_resto} empresas\"."
    if estado.get("cambio") and (_dato(estado, ("pesos", "costo_brecha_anual")) or 0) <= 0:
        limpio["nota_pesos"] = "Su empresa ya pierde igual o menos gente al año que esas empresas: no hay diferencia en pesos a su favor."
    derivadas = cifras_derivadas(estado)
    if derivadas:
        limpio["derivadas"] = derivadas
    return limpio


def _json(dato):
    return json.dumps(dato, ensure_ascii=False, indent=2)


# Cifras que se comparan entre un paso y el siguiente: (nombre para la IA, dónde está en el JSON)
CIFRAS_CLAVE = [
    ("empresas que ya aplican lo que movió", ("grupo", "n")),
    ("parte de su plantilla que esas empresas pierden al año", ("grupo", "indicadores", "rot_anual")),
    ("empresas restantes", ("resto", "n")),
    ("parte de su plantilla que las restantes pierden al año", ("resto", "indicadores", "rot_anual")),
    ("señal", ("senal", "etiqueta")),
    ("completado con empresas similares", ("grupo", "completado")),
    ("costo anual de la medida", ("pesos", "costo_medida_anual")),
    ("diferencia anual en bajas", ("pesos", "costo_brecha_anual")),
]


def _dato(estado, ruta):
    """Busca un valor siguiendo la ruta de llaves; None si falta alguna."""
    for clave in ruta:
        if not isinstance(estado, dict):
            return None
        estado = estado.get(clave)
    return estado


def resumir_cambio(estado, anterior):
    """Una línea por cada cifra clave que cambió: '- nombre: antes X, ahora Y'."""
    lineas = []
    for nombre, ruta in CIFRAS_CLAVE:
        antes, ahora = _dato(anterior, ruta), _dato(estado, ruta)
        if antes != ahora:
            lineas.append(f"- {nombre}: antes {antes}, ahora {ahora}")
    return lineas


def anterior_util(estado, anterior):
    """El paso anterior solo cuenta si es de la misma empresa y ya tenía una palanca movida.

    Otra empresa, o el anterior es el estado inicial (sin palancas movidas, con las 39 empresas):
    decir "antes 39" confunde, así que se trata como primera comparación (None).
    La usan armar_mensaje y la llave del caché, para que las dos sigan la misma regla.
    """
    misma_empresa = _dato(anterior, ("empresa", "id")) == _dato(estado, ("empresa", "id"))
    if not misma_empresa or not _dato(anterior, ("cambio",)):
        return None
    return anterior


def nivel(palanca, valor):
    """('prima_vac_op', 0.5) -> 'prima vacacional de 50%': como se nombra una palanca en el mensaje."""
    formatos = {
        "sal_dia_ini": lambda v: f"${v:,.0f}",
        "aguinaldo_op": lambda v: f"{v:g} días",
        "prima_vac_op": lambda v: f"{v:.0%}",
        "vales_op": lambda v: f"{v * 100:g}%",
        "rutas_x100": lambda v: f"{v:g} por cada 100 operativos",
    }
    return f"{NOMBRES_PALANCA[palanca]} de {formatos[palanca](valor)}"


def cambios_desde(estado, anterior):
    """Qué palancas cambiaron desde la última combinación explicada (el botón Explicar).

    Entre dos pulsaciones el usuario puede mover varias palancas: se comparan las palancas
    movidas de antes y de ahora. Sin paso anterior, se compara contra los valores reales.
    Devuelve (cambios, ya_tenia):
      cambios:  [{"palanca", "de", "a", "tipo"}] con tipo "nueva", "cambiada" o "quitada"
      ya_tenia: {palanca: valor} que no cambiaron desde la última explicación
    "quitada" = volvió a su valor real (deja de filtrar el grupo); su "a" es ese valor real.
    """
    reales = (estado.get("empresa") or {}).get("palancas") or {}
    ahora = estado.get("palancas_movidas") or {}
    antes = (anterior or {}).get("palancas_movidas") or {}
    cambios, ya_tenia = [], {}
    for palanca, valor in ahora.items():
        if palanca not in antes:
            cambios.append({"palanca": palanca, "de": reales.get(palanca), "a": valor, "tipo": "nueva"})
        elif float(antes[palanca]) != float(valor):
            cambios.append({"palanca": palanca, "de": antes[palanca], "a": valor, "tipo": "cambiada"})
        else:
            ya_tenia[palanca] = valor
    for palanca, valor in antes.items():
        if palanca not in ahora:
            cambios.append({"palanca": palanca, "de": valor, "a": reales.get(palanca), "tipo": "quitada"})
    return cambios, ya_tenia


def describir_cambios(estado, anterior):
    """El bloque de texto con los cambios, ya en palabras, para que la IA no tenga que deducirlos."""
    cambios, ya_tenia = cambios_desde(estado, anterior)
    titulo = "Cambios desde la última explicación" if anterior else "Palancas que movió (frente a sus valores reales)"
    lineas = []
    for c in cambios:
        if c["tipo"] == "quitada":
            lineas.append(f"- quitó {NOMBRES_PALANCA[c['palanca']]}: vuelve a su valor real y ya no filtra a las empresas")
        else:
            lineas.append(f"- {nivel(c['palanca'], c['a'])} ({c['tipo']})")
    if not lineas:
        lineas.append("- ninguna palanca cambió")
    texto = f"{titulo}:\n" + "\n".join(lineas)
    if ya_tenia:
        texto += "\nYa tenía: " + ", ".join(nivel(p, v) for p, v in ya_tenia.items())
    return texto


def armar_mensaje(estado, anterior):
    """Arma el mensaje para la IA: qué palancas cambiaron, el estado actual y qué cifras cambiaron.

    `anterior` es la última combinación EXPLICADA (botón Explicar), no el último clic:
    por eso los cambios se calculan con cambios_desde y pueden ser varios.
    """
    anterior = anterior_util(estado, anterior)

    if estado.get("palancas_movidas") or anterior:
        partes = [describir_cambios(estado, anterior)]
    else:
        partes = ["El usuario aún no ha movido ninguna palanca."]
    partes.append(f"Resultado actual:\n{_json(_para_ia(estado))}")
    if anterior:
        lineas = resumir_cambio(estado, anterior) or ["- ninguna cifra clave cambió"]
        partes.append("Qué cambió frente al paso anterior:\n" + "\n".join(lineas))
    else:
        partes.append("No hay paso anterior de esta empresa: es la primera comparación. No compares con pasos anteriores.")
    partes.append("Escribe la explicación.")
    return "\n\n".join(partes)