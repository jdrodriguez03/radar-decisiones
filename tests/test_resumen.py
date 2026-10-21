"""Pruebas del resumen en PDF para el comité (crítica 4). Dueño: Julian.

Revisan tres cosas, en este orden de importancia:
1. Que el PDF no invente cifras: cada número de cada texto existe en el estado (mismo validador
   que la IA), para los 26 pasos del caché y para los casos borde.
2. Que nunca falle la descarga: estados raros, textos con caracteres que la fuente no tiene,
   20 escenarios, «Mi empresa» sin datos, y un PDF de aviso si algo sale mal.
3. Que el botón haga lo que dice: cuántos escenarios lleva, solo los de la empresa en pantalla,
   y que con el interruptor apagado la app quede igual.
"""
import copy
import json
import re
import sys
import zlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import config
from ia.cache import buscar
from ia.resumen import (
    AVISO_COMPLETADO,
    AVISO_ROTAN_MAS,
    INTRODUCCION,
    METODOLOGIA,
    NOTA_TABLA,
    SIN_DATO,
    SIN_EXPLICACION,
    armar_pdf,
    asegurar_cifras,
    combinacion_larga,
    contenido,
    dibujar,
    escenarios_para_resumen,
    latin1,
    nombre_archivo,
    pdf_de_aviso,
    textos_con_cifras,
)
from ia.validador import cifras_inventadas
from motor.api import calcular_estado
from motor.datos import cargar
from scripts.generar_cache import armar_secuencias, cargar_casos, estado_de
from ui import explicacion

RAIZ = Path(__file__).resolve().parents[1]
FECHA = datetime(2026, 10, 21, 10, 45, tzinfo=timezone(timedelta(hours=-5)))
# El caché real, leído una vez: otras pruebas cambian config.RUTA_CACHE por uno temporal.
CACHE = json.loads((Path(__file__).resolve().parents[1] / "data" / "processed" / "cache.json").read_text(encoding="utf-8"))
SUPUESTOS = json.loads(config.RUTA_SUPUESTOS.read_text(encoding="utf-8"))
PALABRAS_PROHIBIDAS = ("logrará", "reducirá", "obtendrá", "garantiza", "provoca", "causa ")


# ---------------------------------------------------------------------------
# Estados reales
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def empresas():
    return cargar()


@pytest.fixture(scope="module")
def caso(empresas):
    """caso("G1") -> el estado real de ese caso de combinaciones.yaml."""
    casos = cargar_casos()
    return lambda nombre: estado_de({"caso": nombre}, casos, empresas, SUPUESTOS)


@pytest.fixture(scope="module")
def todos(empresas):
    """Los estados del caché: guion, respaldos y las 20 combinaciones (26 llaves)."""
    secuencias = armar_secuencias(cargar_casos(), empresas, SUPUESTOS)
    return [e for s in secuencias for e in s]


def guardado(estado, hora="2026-10-21T10:42:05-05:00", texto=None, con_cache=True):
    """Lo mismo que guarda «Guardar escenario» en app.py."""
    if texto is None and con_cache:
        texto = buscar(estado, cache=CACHE)
    return {"hora": hora, "estado": copy.deepcopy(estado), "explicacion": texto}


def con_palancas(estado, empresas, palancas, costo=None, perfil=None):
    """Otro estado de la misma empresa con estas palancas movidas."""
    from ui.selector import perfil_demo

    perfil = perfil or perfil_demo(empresas, estado["empresa"]["id"])
    supuestos = dict(SUPUESTOS, **({"costo_por_baja": costo} if costo else {}))
    ultima = list(palancas)[-1] if palancas else None
    cambio = {"palanca": ultima, "de": perfil["palancas"].get(ultima), "a": palancas[ultima]} if ultima else None
    return calcular_estado(empresas, perfil, dict(palancas), cambio, supuestos)


def texto_pdf(datos_pdf):
    """El texto que escribe el PDF, sacado de sus flujos comprimidos (sin librerías extra)."""
    texto = []
    for flujo in re.findall(rb"stream\r?\n(.*?)\r?\nendstream", datos_pdf, flags=re.DOTALL):
        try:
            crudo = zlib.decompress(flujo)
        except zlib.error:
            crudo = flujo
        for pedazo in re.findall(rb"\((.*?)(?<!\\)\)\s*Tj", crudo, flags=re.DOTALL):
            texto.append(pedazo.replace(rb"\(", b"(").replace(rb"\)", b")").replace(rb"\\", b"\\").decode("latin-1"))
    return re.sub(r" {2,}", " ", " ".join(texto))


# ---------------------------------------------------------------------------
# 1. Ninguna cifra inventada
# ---------------------------------------------------------------------------
def test_cada_cifra_de_los_26_pasos_del_cache_sale_del_estado(todos):
    assert len(todos) >= 26  # 28 estados: dos pasos se repiten, con y sin el paso anterior
    for estado in todos:
        datos = contenido(escenarios_para_resumen(estado, [guardado(estado)]), FECHA)
        for texto in textos_con_cifras(datos, 0):
            assert not cifras_inventadas(texto, estado), (estado["palancas_movidas"], texto)


def test_cada_cifra_del_encabezado_sale_del_estado(caso):
    estado = caso("G3")
    datos = contenido(escenarios_para_resumen(estado, []), FECHA)
    assert not cifras_inventadas(datos["titulo"], estado)
    for etiqueta, valor in datos["situacion"]:
        assert not cifras_inventadas(valor, estado), etiqueta
    assert [v for _, v in datos["situacion"]] == ["1,438 personas", "52%", "$15,000", "$35,000"]


def test_los_casos_borde_tampoco_inventan_cifras(caso, empresas):
    base = caso("G1")
    borde = [
        con_palancas(base, empresas, {"vales_op": 0.06}),  # E5: la medida es un ahorro
        con_palancas(base, empresas, {"rutas_x100": 10.8}),  # E4: ya rota menos, brecha 0
        con_palancas(base, empresas, {"sal_dia_ini": 380}),  # E1: completado
        con_palancas(base, empresas, {"vales_op": 0.065}),  # vales con medio punto
        con_palancas(base, empresas, {"aguinaldo_op": 20}, costo=30000),  # otro supuesto
    ]
    for estado in borde:
        datos = contenido(escenarios_para_resumen(estado, [guardado(estado)]), FECHA)
        for texto in textos_con_cifras(datos, 0):
            assert not cifras_inventadas(texto, estado), (estado["palancas_movidas"], texto)


def test_la_tabla_del_guion_dice_lo_mismo_que_la_app(caso):
    pasos = [caso("G1"), caso("G2"), caso("G3")]
    datos = contenido(escenarios_para_resumen(pasos[-1], [guardado(e) for e in pasos]), FECHA)
    filas = [f["celdas"] for f in datos["filas"]]
    assert filas[0][1:] == ["Aguinaldo de 15 días a 20 días", "22 / 16", "22% vs 53%", "Evidencia clara", "$2.3 M",
                            "$6.3 M"]
    assert filas[1][2:] == ["16 / 22", "17% vs 43%", "Evidencia débil", "$3.7 M", "$7.4 M"]
    assert filas[2][2:] == ["5 / 33", "12% vs 38%", "No concluyente", "$17.6 M", "$8.5 M"]
    assert [f["color"] for f in datos["filas"]] == ["verde", "amarillo", "naranja"]
    assert datos["detalles"][0]["cifras"] == [
        ("Empresas: con / sin la medida", "22 / 16"), ("Rotación: con / sin la medida", "22% / 53%"),
        ("Costo anual de la medida", "$2.3 M"), ("Costo anual de la brecha", "$6.3 M"),
    ]


# ---------------------------------------------------------------------------
# 2. Lenguaje: compara, no promete
# ---------------------------------------------------------------------------
def test_ningun_texto_promete_resultados(todos):
    for estado in todos:
        datos = contenido(escenarios_para_resumen(estado, [guardado(estado)]), FECHA)
        todo = " ".join([datos["titulo"], datos["subtitulo"], INTRODUCCION, NOTA_TABLA, METODOLOGIA]
                        + [c for f in datos["filas"] for c in f["celdas"]]
                        + [t for d in datos["detalles"] for t in textos_con_cifras(datos, 0)]).lower()
        for palabra in PALABRAS_PROHIBIDAS:
            assert palabra not in todo, (palabra, estado["palancas_movidas"])
    assert "no constituyen una proyección" in INTRODUCCION


def test_si_las_que_lo_hacen_rotan_mas_se_dice_y_va_en_rojo(caso, empresas):
    estado = con_palancas(caso("G1"), empresas, {"rutas_x100": 10.8})  # E4: 60% contra 29%
    datos = contenido(escenarios_para_resumen(estado, [guardado(estado)]), FECHA)
    assert datos["filas"][0]["rotan_mas"] is True
    assert datos["detalles"][0]["consideraciones"][0] == ("rojo", AVISO_ROTAN_MAS)


def test_el_grupo_completado_lleva_su_aviso(caso, empresas):
    estado = con_palancas(caso("G1"), empresas, {"sal_dia_ini": 380})  # E1
    datos = contenido(escenarios_para_resumen(estado, [guardado(estado)]), FECHA)
    assert datos["filas"][0]["celdas"][2].endswith(" *")
    assert "completado con similares" in datos["detalles"][0]["solidez"]
    # La interpretación del caché ya lo advierte: no se repite en las consideraciones
    sin_texto = contenido(escenarios_para_resumen(estado, [guardado(estado, con_cache=False)]), FECHA)
    assert ("", AVISO_COMPLETADO) in sin_texto["detalles"][0]["consideraciones"]


def test_ahorro_y_brecha_cero_se_escriben_claro(caso, empresas):
    ahorro = con_palancas(caso("G1"), empresas, {"vales_op": 0.06})
    sin_brecha = con_palancas(caso("G1"), empresas, {"rutas_x100": 10.8})
    datos = contenido(escenarios_para_resumen(ahorro, [guardado(ahorro), guardado(sin_brecha)]), FECHA)
    assert datos["filas"][0]["celdas"][5] == "Ahorro $5.1 M"
    assert dict(datos["detalles"][0]["cifras"])["Costo anual de la medida"] == "Ahorro de $5.1 M"
    assert datos["filas"][1]["celdas"][6] == "-"
    assert dict(datos["detalles"][1]["cifras"])["Costo anual de la brecha"] == "Sin brecha"


# ---------------------------------------------------------------------------
# 3. Qué escenarios entran
# ---------------------------------------------------------------------------
def test_sin_guardados_entra_el_de_pantalla_con_su_explicacion(caso):
    estado = caso("G1")
    escenarios = escenarios_para_resumen(estado, [], texto_actual="Texto de prueba.")
    assert len(escenarios) == 1
    assert escenarios[0]["estado"] is estado
    assert escenarios[0]["explicacion"] == "Texto de prueba."
    assert escenarios_para_resumen(estado, None)[0]["explicacion"] is None


def test_solo_entran_los_de_la_empresa_en_pantalla(caso):
    c36, c29 = caso("G1"), caso("R29-1")
    escenarios = escenarios_para_resumen(c36, [guardado(c29), guardado(c36), guardado(c29)])
    assert [e["estado"]["empresa"]["id"] for e in escenarios] == ["COMPAÑIA 36"]
    # Si de esta empresa no hay ninguno guardado, entra el de pantalla
    assert escenarios_para_resumen(caso("R15-1"), [guardado(c36)])[0]["estado"]["empresa"]["id"] == "COMPAÑIA 15"


def test_un_escenario_guardado_dos_veces_sale_una_vez_y_conserva_su_explicacion(caso):
    g1, g2 = caso("G1"), caso("G2")
    lista = [
        guardado(g1, texto="Primera explicación."),
        guardado(g2),
        guardado(g1, hora="2026-10-21T10:50:00-05:00", con_cache=False),  # otra vez, sin explicación
    ]
    escenarios = escenarios_para_resumen(g2, lista)
    assert [e["estado"]["palancas_movidas"] for e in escenarios] == [g1["palancas_movidas"], g2["palancas_movidas"]]
    assert escenarios[0]["explicacion"] == "Primera explicación."
    assert escenarios[0]["hora"] == "2026-10-21T10:50:00-05:00"


def test_mismo_escenario_con_otro_costo_por_baja_son_dos(caso, empresas):
    g1 = caso("G1")
    caro = con_palancas(g1, empresas, {"aguinaldo_op": 20}, costo=30000)
    datos = contenido(escenarios_para_resumen(g1, [guardado(g1), guardado(caro)]), FECHA)
    assert len(datos["filas"]) == 2
    assert dict(datos["situacion"])["Costo por baja *"] == "Varía por escenario"
    assert datos["detalles"][1]["supuestos"].startswith("$30,000 por baja")


def test_sin_explicacion_lo_dice(caso):
    g1 = caso("G1")
    datos = contenido(escenarios_para_resumen(g1, [guardado(g1, con_cache=False)]), FECHA)
    assert datos["detalles"][0]["interpretacion"] == SIN_EXPLICACION
    assert datos["detalles"][0]["con_explicacion"] is False


def test_la_situacion_actual_sin_cambios_no_rompe_nada(caso, empresas):
    inicial = con_palancas(caso("G1"), empresas, {})
    datos = contenido(escenarios_para_resumen(inicial, [guardado(inicial, con_cache=False)]), FECHA)
    assert datos["filas"][0]["celdas"][1] == "Situación actual (sin cambios)"
    assert datos["filas"][0]["celdas"][3:] == ["-", "-", "-", "-"]
    assert dibujar(datos).startswith(b"%PDF")


def test_si_todas_cumplen_la_combinacion_lo_dice_sin_romperse(caso, empresas):
    estado = con_palancas(caso("G1"), empresas, {"aguinaldo_op": 15.0, "prima_vac_op": 0.25})  # resto vacío
    datos = contenido(escenarios_para_resumen(estado, [guardado(estado, con_cache=False)]), FECHA)
    assert datos["filas"][0]["celdas"][4] == "Sin comparación"
    assert datos["detalles"][0]["consideraciones"][0][1].startswith("No es posible comparar")
    for texto in textos_con_cifras(datos, 0):
        assert not cifras_inventadas(texto, estado), texto
    assert dibujar(datos).startswith(b"%PDF")


def test_mi_empresa_sin_algunos_datos_tambien_sale(empresas):
    perfil = {
        "id": "MI EMPRESA", "plantilla_op": 300,
        "palancas": {"sal_dia_ini": 300, "aguinaldo_op": 15, "prima_vac_op": 0.25},  # sin vales ni rutas
        "indicadores": {"rot_anual": 0.6, "rot_temprana": None, "ausentismo": None},
    }
    estado = calcular_estado(empresas, perfil, {"aguinaldo_op": 20},
                             {"palanca": "aguinaldo_op", "de": 15, "a": 20}, SUPUESTOS)
    datos = contenido(escenarios_para_resumen(estado, []), FECHA)
    assert datos["titulo"].endswith("MI EMPRESA")
    assert dict(datos["situacion"])["Plantilla operativa"] == "300 personas"
    assert combinacion_larga(estado) == "Aguinaldo de 15 días a 20 días"
    assert dibujar(datos).startswith(b"%PDF")


# ---------------------------------------------------------------------------
# 4. El PDF en sí
# ---------------------------------------------------------------------------
def test_el_pdf_es_valido_tamano_carta_y_dice_lo_que_debe(caso):
    pasos = [caso("G1"), caso("G2"), caso("G3")]
    pdf, total = armar_pdf(pasos[-1], [guardado(e) for e in pasos], fecha=FECHA)
    assert total == 3
    assert pdf.startswith(b"%PDF-") and pdf.rstrip().endswith(b"%%EOF")
    assert b"/MediaBox [0 0 612.00 792.00]" in pdf  # carta: 8.5 x 11 pulgadas
    texto = texto_pdf(pdf)
    for esperado in ("Escenarios de compensación: COMPAÑIA 36", "21 de octubre de 2026",
                     "SITUACIÓN ACTUAL DE LA COMPAÑÍA", "1,438 personas", "$15,000",
                     "1. Resumen de escenarios", "Aguinaldo de 15 días a 20 días", "22% vs 53%", "Evidencia clara",
                     "2. Detalle por escenario", "2.3", "Escenario registrado a las 10:42", "INTERPRETACIÓN",
                     "3. Nota metodológica", "no constituyen una proyección", "Página 1 de"):
        assert esperado in texto, esperado
    assert "Confidencial" not in texto
    explicacion_g1 = buscar(pasos[0], cache=CACHE)
    assert explicacion_g1 and explicacion_g1[:60] in texto  # la explicación guardada sale tal cual


def test_veinte_escenarios_hacen_varias_hojas_sin_romperse(todos):
    c36 = [e for e in todos if e["empresa"]["id"] == "COMPAÑIA 36"]
    lista = [guardado(e, hora=f"2026-10-21T10:{i:02d}:00-05:00") for i, e in enumerate(c36)]
    pdf, total = armar_pdf(c36[-1], lista, fecha=FECHA)
    assert total == len({json.dumps([e["palancas_movidas"], e["pesos"]["supuestos"]], sort_keys=True) for e in c36})
    hojas = len(re.findall(rb"/Type /Page\b", pdf))
    assert hojas >= 3
    assert f"Página {hojas} de {hojas}" in texto_pdf(pdf)


def test_caracteres_que_la_fuente_no_tiene_no_rompen_la_descarga(caso):
    g1 = caso("G1")
    raro = "Rotan menos — mucho → ≥ 20 días “así” … ⚠ 😀 汉 ŝ fin"
    pdf, _ = armar_pdf(g1, [guardado(g1, texto=raro)], fecha=FECHA)
    texto = texto_pdf(pdf)
    assert "Rotan menos - mucho -> >= 20 días \"así\" ... s fin" in texto


def test_latin1_conserva_acentos_y_quita_lo_demas():
    assert latin1("Compañía ¿Ñu? «sí» · $1,438") == "Compañía ¿Ñu? «sí» · $1,438"
    assert latin1("a — b") == "a - b"
    assert latin1("😀 hola") == " hola"


def test_todos_los_textos_del_cache_caben_en_la_fuente_sin_perder_letras():
    for valor in CACHE.values():
        assert latin1(valor["texto"]) == valor["texto"]


def test_nombre_de_archivo_sin_acentos_ni_espacios(caso):
    assert nombre_archivo(caso("G1"), FECHA) == "Radar_COMPANIA-36_2026-10-21.pdf"
    assert nombre_archivo({"empresa": {"id": "MI EMPRESA"}}, FECHA) == "Radar_MI-EMPRESA_2026-10-21.pdf"
    assert nombre_archivo({}, FECHA) == "Radar_empresa_2026-10-21.pdf"


def test_el_pdf_de_aviso_tambien_es_un_pdf():
    pdf = pdf_de_aviso()
    assert pdf.startswith(b"%PDF-")
    assert "No se pudo generar el informe" in texto_pdf(pdf)


def test_si_una_cifra_no_estuviera_en_los_datos_no_se_imprime(caso):
    """La validación al descargar: un texto con un número inventado se cambia por SIN_DATO."""
    g1 = caso("G1")
    escenarios = escenarios_para_resumen(g1, [guardado(g1)])
    datos = contenido(escenarios, FECHA)
    datos["filas"][0]["celdas"][3] = "97% vs 53%"  # 97 no sale del estado
    datos["detalles"][0]["cifras"][1] = ("Rotación: con / sin la medida", "97% / 53%")
    datos["detalles"][0]["consideraciones"].append(("", "Dato inventado: 777 empresas."))
    datos["situacion"][0] = ("Plantilla operativa", "9,999 personas")
    seguro = asegurar_cifras(datos, escenarios)
    assert seguro["filas"][0]["celdas"][3] == SIN_DATO
    assert seguro["detalles"][0]["cifras"][1] == ("Rotación: con / sin la medida", SIN_DATO)
    assert seguro["detalles"][0]["consideraciones"][-1] == ("", SIN_DATO)
    assert seguro["situacion"][0] == ("Plantilla operativa", SIN_DATO)
    assert seguro["filas"][0]["celdas"][2] == "22 / 16"  # lo correcto no se toca


def test_la_validacion_no_borra_nada_en_los_pasos_reales(todos):
    for estado in todos:
        escenarios = escenarios_para_resumen(estado, [guardado(estado)])
        datos = asegurar_cifras(contenido(escenarios, FECHA), escenarios)
        assert SIN_DATO not in json.dumps(datos, ensure_ascii=False), estado["palancas_movidas"]


# ---------------------------------------------------------------------------
# 5. El botón
# ---------------------------------------------------------------------------
def test_si_falla_el_armado_baja_el_pdf_de_aviso(monkeypatch, caso):
    import ia.resumen

    def falla(*_):
        raise RuntimeError("algo raro")

    monkeypatch.setattr(ia.resumen, "armar_pdf", falla)
    pdf = explicacion._pdf_seguro(caso("G1"), [], None, FECHA)
    assert "No se pudo generar el informe" in texto_pdf(pdf)


def test_sin_la_libreria_no_dibuja_el_boton(monkeypatch, caso):
    monkeypatch.setitem(sys.modules, "fpdf", None)  # así se ve un import que falla
    assert explicacion.boton_resumen(None, caso("G1"), []) is False


def test_la_explicacion_de_pantalla_entra_solo_si_esta_al_dia(caso):
    g1, g2 = caso("G1"), caso("G2")
    explicado = dict(copy.deepcopy(g1), explicacion={"fuente": "cache", "texto": "Texto de G1."})
    assert explicacion._texto_vigente(g1, explicado) == "Texto de G1."
    assert explicacion._texto_vigente(g2, explicado) is None
    assert explicacion._texto_vigente(g1, None) is None


def _app_boton(guardados_json):
    """App mínima con solo el botón, para probarlo con AppTest."""
    import json as _json

    import streamlit as st

    from ui import explicacion as panel

    datos = _json.loads(guardados_json)
    panel.boton_resumen(st.container(), datos["actual"], datos["guardados"])


def test_el_boton_dice_cuantos_escenarios_lleva(caso):
    pasos = [caso("G1"), caso("G2")]
    datos = json.dumps({"actual": pasos[-1], "guardados": [guardado(e) for e in pasos]}, ensure_ascii=False)
    at = AppTest.from_function(_app_boton, args=(datos,), default_timeout=60).run()
    assert not at.exception
    botones = at.get("download_button")
    assert len(botones) == 1
    assert botones[0].proto.label == "Descargar resumen (PDF) · 2 escenarios"


def test_si_guardo_el_mismo_escenario_varias_veces_el_boton_lo_aclara(caso):
    g1 = caso("G1")
    datos = json.dumps({"actual": g1, "guardados": [guardado(g1)] * 3}, ensure_ascii=False)
    at = AppTest.from_function(_app_boton, args=(datos,), default_timeout=60).run()
    assert at.get("download_button")[0].proto.label == "Descargar resumen (PDF) · 1 escenario sin repetir"


# ---------------------------------------------------------------------------
# 6. En la app completa (solo cuando app.py ya tiene EXTRAS["resumen"])
# ---------------------------------------------------------------------------
TIENE_RESUMEN = '"resumen"' in (RAIZ / "app.py").read_text(encoding="utf-8")


def _etiquetas_descarga(at):
    return [b.proto.label for b in at.get("download_button")]


@pytest.mark.skipif(not TIENE_RESUMEN, reason="app.py aún no conecta EXTRAS['resumen'] (lo hace Gaby)")
def test_en_la_app_guardar_dos_escenarios_los_lleva_al_resumen():
    at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=60).run()
    assert not at.exception
    assert _etiquetas_descarga(at) == ["Descargar resumen (PDF) · 1 escenario"]  # el de pantalla
    for _ in range(5):
        next(b for b in at.button if b.key == "mas_aguinaldo_op").click().run()
    next(b for b in at.button if b.key == "btn_guardar").click().run()
    next(b for b in at.button if b.key == "mas_prima_vac_op").click().run()
    next(b for b in at.button if b.key == "btn_guardar").click().run()
    assert not at.exception
    assert _etiquetas_descarga(at) == ["Descargar resumen (PDF) · 2 escenarios"]
    guardados = at.session_state["escenarios_guardados"]
    estado_actual = guardados[-1]["estado"]
    pdf, total = armar_pdf(estado_actual, guardados, fecha=FECHA)
    assert total == 2 and pdf.startswith(b"%PDF-")


@pytest.mark.skipif(not TIENE_RESUMEN, reason="app.py aún no conecta EXTRAS['resumen'] (lo hace Gaby)")
def test_con_el_interruptor_apagado_no_aparece_el_boton(tmp_path):
    fuente = (RAIZ / "app.py").read_text(encoding="utf-8")
    apagado = fuente.replace('"resumen": True', '"resumen": False', 1)
    assert apagado != fuente
    copia = tmp_path / "app.py"
    copia.write_text(apagado, encoding="utf-8")
    sys.path.insert(0, str(RAIZ))  # la copia vive en otra carpeta y necesita importar config, motor y ui
    at = AppTest.from_file(str(copia), default_timeout=60).run()
    assert not at.exception
    next(b for b in at.button if b.key == "btn_guardar").click().run()
    assert not at.exception
    assert _etiquetas_descarga(at) == []


def test_el_pdf_se_arma_antes_y_solo_se_rehace_si_algo_cambia(monkeypatch, caso):
    """El PDF va listo en el botón (sin funciones pendientes que Streamlit pueda perder entre recargas)."""
    llamadas = []
    original = explicacion._pdf_seguro

    def contar(*args):
        llamadas.append(1)
        return original(*args)

    monkeypatch.setattr(explicacion, "_pdf_seguro", contar)
    g1, g2 = caso("G1"), caso("G2")
    memoria, lista = {}, [guardado(g1)]
    escenarios = escenarios_para_resumen(g1, lista)
    pdf = explicacion.pdf_en_memoria(memoria, escenarios, g1, lista, None, FECHA)
    assert pdf.startswith(b"%PDF-") and len(llamadas) == 1
    explicacion.pdf_en_memoria(memoria, escenarios, g1, lista, None, FECHA)  # nada cambió: no se rehace
    assert len(llamadas) == 1
    lista.append(guardado(g2))  # un escenario más: se rehace
    escenarios = escenarios_para_resumen(g2, lista)
    otro = explicacion.pdf_en_memoria(memoria, escenarios, g2, lista, None, FECHA)
    assert len(llamadas) == 2 and otro != pdf


def test_las_diferencias_no_se_presentan_como_algo_en_comun(caso):
    """El motor da las mayores DIFERENCIAS entre grupo y resto, en cualquier sentido (0 de 5 frente a 13 de 33)."""
    g3 = caso("G3")
    datos = contenido(escenarios_para_resumen(g3, [guardado(g3)]), FECHA)
    lineas = [texto for _, texto in datos["detalles"][0]["consideraciones"]]
    assert "Diferencia con las empresas sin la medida: manejan jornadas de 12 horas (0 de 5 con la medida, frente a 13 de 33 sin ella)." in lineas
    assert ("Diferencia con las empresas sin la medida: motivo de baja por cuidado de hijos o familiares (10% con la medida, "
            "frente a 50% sin ella).") in lineas
    todo = " ".join(lineas).lower()
    assert "en común" not in todo and "común del grupo" not in todo
    assert ": " not in " ".join(linea.removeprefix("Diferencia con las empresas sin la medida: ") for linea in lineas)  # sin dos puntos dobles
