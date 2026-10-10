import json

from config import RUTA_FIXTURES
from ia.prompts import armar_mensaje, como_decirlo, rasgos_utiles, resumir_cambio


def cargar(nombre):
    return json.loads((RUTA_FIXTURES / f"{nombre}.json").read_text(encoding="utf-8"))


def test_primera_comparacion_no_compara():
    mensaje = armar_mensaje(cargar("01_aguinaldo"), None)
    assert "Qué cambió" not in mensaje
    assert "primera comparación" in mensaje


def test_con_paso_anterior_dice_que_cambio():
    mensaje = armar_mensaje(cargar("02_prima"), cargar("01_aguinaldo"))
    assert "Qué cambió frente al paso anterior" in mensaje
    assert "antes 22, ahora 16" in mensaje  # empresas que ya lo hacen
    assert "antes 0.222, ahora 0.174" in mensaje  # lo que pierden al año
    assert "antes clara, ahora débil" in mensaje  # la señal


def test_solo_lista_lo_que_cambio():
    lineas = resumir_cambio(cargar("02_prima"), cargar("01_aguinaldo"))
    assert not any("completado" in linea for linea in lineas)  # era False y sigue False


def test_otra_empresa_no_se_compara():
    anterior = cargar("01_aguinaldo")
    anterior["empresa"]["id"] = "COMPAÑIA 29"
    mensaje = armar_mensaje(cargar("02_prima"), anterior)
    assert "Qué cambió" not in mensaje


def test_estado_inicial_sin_cambio():
    mensaje = armar_mensaje(cargar("05_inicial"), None)
    assert "aún no ha movido ninguna palanca" in mensaje


def test_no_manda_las_listas_de_ids():
    mensaje = armar_mensaje(cargar("02_prima"), cargar("01_aguinaldo"))
    assert '"ids"' not in mensaje


def test_como_decirlo_con_conteos():
    assert como_decirlo({"grupo": "16 de 16", "resto": "4 de 22"}) == "todas"
    assert como_decirlo({"grupo": "16 de 22", "resto": "4 de 16"}) == "la mayoría"
    assert como_decirlo({"grupo": "2 de 22", "resto": "4 de 16"}) == "pocas"


def test_como_decirlo_con_medianas_nunca_dice_todas():
    assert como_decirlo({"grupo": 332.0, "resto": 289.0}) == "suelen tener un valor más alto que las demás"
    assert como_decirlo({"grupo": 280, "resto": 300}) == "suelen tener un valor más bajo que las demás"
    assert como_decirlo({"grupo": 321, "resto": 322}) == "tienen un valor parecido al de las demás"


def test_el_mensaje_lleva_como_decirlo():
    mensaje = armar_mensaje(cargar("02_prima"), cargar("01_aguinaldo"))
    assert '"como_decirlo": "suelen tener un valor más alto que las demás"' in mensaje


def test_quita_los_rasgos_de_palancas_movidas():
    # en el paso 02 se movieron aguinaldo y prima: "prima de 50% o más, 16 de 16" es obvio
    textos = [r["texto"] for r in rasgos_utiles(cargar("02_prima"))]
    assert textos == ["salario inicial mediano"]
    # en el 03 también se movió el salario: no queda ningún rasgo útil
    assert rasgos_utiles(cargar("03_salario")) == []
    # en el 01 solo se movió el aguinaldo: la prima sí dice algo nuevo
    assert rasgos_utiles(cargar("01_aguinaldo"))[0]["texto"] == "prima vacacional de 50% o más"


def test_la_ia_recibe_un_solo_rasgo():
    mensaje = armar_mensaje(cargar("02_prima"), cargar("01_aguinaldo"))
    assert "prima vacacional de 50% o más" not in mensaje
    assert mensaje.count('"como_decirlo"') == 1

def test_si_ya_pierde_menos_llega_la_nota():
    assert '"nota_pesos"' in armar_mensaje(cargar("04_ya_rota_menos"), None)
    assert '"nota_pesos"' not in armar_mensaje(cargar("02_prima"), cargar("01_aguinaldo"))
    assert '"nota_pesos"' not in armar_mensaje(cargar("05_inicial"), None)  # sin cambio no hay medida


def test_el_estado_inicial_no_cuenta_como_paso_anterior():
    mensaje = armar_mensaje(cargar("01_aguinaldo"), cargar("05_inicial"))
    assert "Qué cambió" not in mensaje  # no debe decir "antes 39"
    assert "primera comparación" in mensaje



def test_el_mensaje_lleva_las_metricas_precalculadas():
    mensaje = armar_mensaje(cargar("01_aguinaldo"), None)
    assert '"derivadas"' in mensaje
    assert '"porcentaje_de_la_nomina_base"' in mensaje


def test_el_prompt_pide_maximo_75_palabras_y_sin_cuentas_propias():
    from ia.prompts import PROMPT_SISTEMA

    assert "máximo 75 palabras" in PROMPT_SISTEMA
    assert "No hagas cuentas propias" in PROMPT_SISTEMA
    assert "1 de cada 2" in PROMPT_SISTEMA  # la regla que pide decir "la mitad" con palabras
