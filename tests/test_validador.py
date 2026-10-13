import json

import pytest

from config import RUTA_EJEMPLO, RUTA_FIXTURES
from ia.plantilla import plantilla
from ia.validador import cifras_inventadas, es_valido, extraer_numeros


def cargar(nombre=None):
    ruta = RUTA_FIXTURES / nombre if nombre else RUTA_EJEMPLO
    return json.loads(ruta.read_text(encoding="utf-8"))


# --- Las dos pruebas del "Listo cuando" del día 5 ---

def test_texto_correcto_pasa():
    texto = (
        "Las 22 empresas que ya dan 20 días de aguinaldo o más pierden 22% de su plantilla al año; "
        "las demás, 53%. Para su empresa, esa diferencia equivale a $6.3 millones de pesos al año, "
        "contra $2.3 millones de pesos que costaría la medida."
    )
    assert es_valido(texto, cargar())


def test_porcentaje_inventado_falla():
    # 31% = 53 - 22: una resta que la IA hace por su cuenta y que no está en el JSON
    texto = "Esas 22 empresas pierden 31 puntos menos de su plantilla al año."
    assert not es_valido(texto, cargar())
    assert cifras_inventadas(texto, cargar()) == [31.0]


def test_cifra_real_en_otro_lugar_pasa():
    # Límite conocido: 25% existe en el JSON (la prima actual, 0.25), así que pasa aunque
    # la IA lo use como rotación. El validador revisa que la cifra exista, no en qué frase va.
    assert es_valido("Esas empresas pierden 25% de su plantilla al año.", cargar())


# --- Piezas sueltas ---

def test_extraer_numeros():
    assert extraer_numeros("pierden 22%, $6.3 millones, plantilla de 1,438 y 16 de 22.") == [
        22.0, 6.3, 1438.0, 16.0, 22.0,
    ]


def test_los_ids_de_otras_empresas_no_cuentan():
    # El 7 solo aparece como "COMPAÑIA 7" dentro de resto.ids: no es una cifra válida
    assert not es_valido("Hay 7 empresas.", cargar("03_salario.json"))


def test_cifra_del_paso_anterior_necesita_el_anterior():
    # 53% es lo que perdía el resto en el paso 01; en el paso 02 ningún valor da 53.
    # (No sirve "antes 22": en el paso 02 resto.n también es 22, y pasaría por coincidencia.)
    texto = "Las demás pierden 43% de su plantilla al año, antes 53%."
    estado, anterior = cargar("02_prima.json"), cargar("01_aguinaldo.json")
    assert cifras_inventadas(texto, estado) == [53.0]
    assert es_valido(texto, estado, anterior)


# --- Los textos reales de claude-sonnet-5-5 guardados en docs/pruebas_ia.md ---

TEXTOS_REALES = [
    (
        "01_aguinaldo.json", None,
        (
            "Las 22 empresas que ya dan 20 días de aguinaldo o más pierden 22% de su plantilla al año; las demás, 53%. "
            "Para su empresa, que hoy pierde 52%, esa diferencia equivale a $6.3 millones de pesos al año en bajas, "
            "contra $2.3 millones de pesos que costaría la medida. Además, la mayoría de esas empresas también da "
            "prima vacacional de 50% o más."
        ),
    ),
    (
        "02_prima.json", "01_aguinaldo.json",
        (
            "Con la prima vacacional de 50% y el aguinaldo de 20 días, quedan 16 empresas, antes 22; pierden 17% de su "
            "plantilla al año y las demás, 43%. Para su empresa, que hoy pierde 52%, la diferencia equivale a $7.4 "
            "millones de pesos al año en bajas, contra $3.7 millones de la medida. Además, esas empresas suelen tener "
            "un salario inicial más alto, aunque la señal es débil."
        ),
    ),
    (
        "03_salario.json", "02_prima.json",
        (
            "Con el salario inicial de $350 diarios, la prima vacacional de 50% y el aguinaldo de 20 días, quedan 5 "
            "empresas, antes 16; pierden 12% de su plantilla al año y las demás, 38%. Para su empresa, la diferencia "
            "equivale a $8.5 millones de pesos al año en bajas, contra $17.6 millones de la medida."
        ),
    ),
    (
        "04_ya_rota_menos.json", None,
        (
            "Las 7 empresas que ya dan vales de 12% o más pierden 42% de su plantilla al año; las demás, 34%. "
            "Para su empresa, que hoy pierde 4% al año, no hay diferencia en pesos a su favor."
        ),
    ),
    (
        "05_inicial.json", None,
        (
            "Hoy su empresa pierde 52% de su plantilla al año, mientras que las 39 empresas de la encuesta pierden 36%. "
            "Esa diferencia equivale a $3.4 millones de pesos al año en bajas."
        ),
    ),
]


@pytest.mark.parametrize("fixture, anterior, texto", TEXTOS_REALES)
def test_textos_reales_pasan(fixture, anterior, texto):
    estado = cargar(fixture)
    previo = cargar(anterior) if anterior else None
    assert cifras_inventadas(texto, estado, previo) == []


# --- La plantilla es el respaldo: ella misma nunca debe fallar el validador ---

@pytest.mark.parametrize("fixture", sorted(p.name for p in RUTA_FIXTURES.glob("*.json")))
def test_la_plantilla_siempre_pasa(fixture):
    estado = cargar(fixture)
    assert es_valido(plantilla(estado), estado)


def test_la_plantilla_con_rutas_pasa():
    # "por cada 100 operativos": el 100 es texto fijo, no una cifra inventada
    estado = cargar()
    estado["cambio"] = {"palanca": "rutas_x100", "de": 2.85, "a": 3}
    estado["palancas_movidas"] = {"rutas_x100": 3}
    assert es_valido(plantilla(estado), estado)

# --- Las tres aperturas: métricas precalculadas, números del idioma y redondeo hacia abajo ---

def test_acepta_las_metricas_precalculadas():
    texto = "22 de las 38 empresas comparables, 58%, ya lo hacen; la medida suma 1.4% a la nómina base."
    assert es_valido(texto, cargar("01_aguinaldo.json"))


def test_una_cuenta_que_no_esta_en_la_lista_sigue_fallando():
    # 319 = 1,438 × 0.222: cierta, pero no está entre las métricas precalculadas
    assert cifras_inventadas("Esas empresas perderían unas 319 personas.", cargar("01_aguinaldo.json")) == [319.0]


def test_acepta_los_numeros_del_idioma():
    texto = "De cada 100 operativos, 52 se van al año; unas 297 personas se van antes de 3 meses, en 12 meses."
    assert es_valido(texto, cargar("01_aguinaldo.json"))


def test_acepta_redondear_hacia_abajo_pero_no_mas():
    estado = cargar()  # la empresa pierde 0.516
    assert es_valido("Su empresa pierde 51% de su plantilla al año.", estado)  # hacia abajo
    assert es_valido("Su empresa pierde 52% de su plantilla al año.", estado)  # al más cercano
    # 49 ya no es redondeo: es otra cifra (y no sirve 50, que existe: la rotación temprana del grupo es 0.50)
    assert not es_valido("Su empresa pierde 49% de su plantilla al año.", estado)


def test_el_redondeo_hacia_abajo_no_se_confunde_con_decimales_raros():
    # 0.29 * 100 da 28.999999999999996 en Python; sin limpiarlo, "hacia abajo" daría 28
    estado = cargar()
    estado["grupo"]["indicadores"]["rot_anual"] = 0.29
    assert cifras_inventadas("Esas empresas pierden 29%; ninguna 28%.", estado) == [28.0]
