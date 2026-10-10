import json

from config import RUTA_FIXTURES
from ia.derivadas import cifras_derivadas


def cargar(nombre):
    return json.loads((RUTA_FIXTURES / f"{nombre}.json").read_text(encoding="utf-8"))


def valores(nombre):
    return {clave: d["valor"] for clave, d in cifras_derivadas(cargar(nombre)).items()}


# --- Las cifras del guion ---

def test_paso_del_aguinaldo():
    assert valores("01_aguinaldo") == {
        "personas_que_pierde_al_año": 742,
        "personas_que_se_van_antes_de_3_meses": 297,
        "empresas_comparables": 38,
        "porcentaje_que_ya_lo_hace": 58,
        "porcentaje_de_la_nomina_base": 1.4,
        "personas_de_diferencia_al_año": 423,
    }


def test_el_salario_cuesta_mucho_mas_de_la_nomina():
    # El mensaje de eficiencia de la demo: 1.4% con aguinaldo contra 10.3% con salario
    assert valores("03_salario")["porcentaje_de_la_nomina_base"] == 10.3
    assert valores("03_salario")["porcentaje_que_ya_lo_hace"] == 13


# --- Cuándo una métrica no aplica ---

def test_estado_inicial_solo_dice_el_tamano_del_problema():
    v = valores("05_inicial")
    assert "porcentaje_que_ya_lo_hace" not in v  # daría "39 de 39"
    assert "porcentaje_de_la_nomina_base" not in v  # no hay medida
    assert v["personas_que_pierde_al_año"] == 742


def test_si_ya_pierde_menos_no_hay_personas_de_diferencia():
    assert "personas_de_diferencia_al_año" not in valores("04_ya_rota_menos")


def test_grupo_completado_no_dice_que_tan_comun_es():
    estado = cargar("03_salario")
    estado["grupo"]["completado"] = True
    assert "porcentaje_que_ya_lo_hace" not in cifras_derivadas(estado)


def test_mi_empresa_sin_rotacion_temprana_no_se_rompe():
    estado = cargar("01_aguinaldo")
    estado["empresa"]["indicadores"]["rot_temprana"] = None
    assert "personas_que_se_van_antes_de_3_meses" not in cifras_derivadas(estado)


def test_las_personas_no_dependen_del_costo_por_baja():
    estado = cargar("01_aguinaldo")
    estado["pesos"]["supuestos"]["costo_por_baja"] = 30000
    estado["pesos"]["costo_brecha_anual"] *= 2
    assert cifras_derivadas(estado)["personas_de_diferencia_al_año"]["valor"] == 423
