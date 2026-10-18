"""Interruptores de extras en app.py (día 11). Dueño: Gaby.

Listo cuando: cada extra se apaga con un solo cambio y, con todos en False, la app queda como el día 8.
Cada prueba corre una copia de app.py con el diccionario EXTRAS cambiado, sin tocar el archivo real.
"""
import re
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from ui import escenarios, historial

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))  # la copia vive en otra carpeta y necesita importar config, motor y ui

PATRON = re.compile(r"^EXTRAS = \{.*?^\}", flags=re.DOTALL | re.MULTILINE)  # el bloque del diccionario
TODOS = ("escenarios", "historial", "tamano_parecido", "semaforo")
FALTA_ESCENARIOS = pytest.mark.skipif(not hasattr(escenarios, "guardar"), reason="ui/escenarios.py aún no está en main")
FALTA_HISTORIAL = pytest.mark.skipif(not hasattr(historial, "agregar"), reason="ui/historial.py aún no está en main")


def app_con(tmp_path, **extras):
    """Copia app.py con EXTRAS reemplazado y devuelve la app ya cargada."""
    fuente = (RAIZ / "app.py").read_text(encoding="utf-8")
    assert PATRON.search(fuente), "app.py debe tener el diccionario EXTRAS"
    nuevo = "EXTRAS = " + repr({k: extras.get(k, False) for k in TODOS})
    copia = tmp_path / "app.py"
    copia.write_text(PATRON.sub(lambda _: nuevo, fuente, count=1), encoding="utf-8")
    return AppTest.from_file(str(copia), default_timeout=60).run()


def boton(at, clave):
    return next(b for b in at.button if b.key == clave)


def textos(at):
    return " ".join(m.value for m in at.markdown)


def subir_aguinaldo(at, veces):
    for _ in range(veces):
        boton(at, "mas_aguinaldo_op").click().run()


def test_el_diccionario_tiene_los_extras_y_no_la_pregunta_libre():
    fuente = (RAIZ / "app.py").read_text(encoding="utf-8")
    bloque = PATRON.search(fuente).group(0)
    for extra in TODOS:
        assert f'"{extra}"' in bloque
    assert "pregunta_libre" not in bloque


def test_con_todo_apagado_la_app_queda_como_el_dia_8(tmp_path):
    at = app_con(tmp_path)
    subir_aguinaldo(at, 5)
    assert not at.exception
    assert not at.toggle  # no aparece el interruptor de tamaño
    assert "semaforo-direccion" not in textos(at)
    assert not [e for e in at.expander if e.label == "Historial de cambios"]
    assert "Comparando con 22 empresas reales" in textos(at)  # paso 1 del guion intacto
    boton(at, "btn_guardar").click().run()
    assert not [b for b in at.button if b.key == "btn_limpiar_ab"]


def test_tamano_parecido_reduce_el_grupo_a_la_misma_banda(tmp_path):
    at = app_con(tmp_path, tamano_parecido=True)
    subir_aguinaldo(at, 5)
    assert "Comparando con 22 empresas reales" in textos(at)
    at.toggle(key="solo_tamano").set_value(True).run()
    assert not at.exception
    assert "Comparando con 9 empresas reales" in textos(at)  # solo empresas grandes, como COMPAÑIA 36


def test_tamano_parecido_con_una_plantilla_sin_banda_compara_con_todas(tmp_path):
    at = app_con(tmp_path, tamano_parecido=True)
    at.toggle(key="solo_tamano").set_value(True).run()
    at.radio[0].set_value("Mi empresa").run()
    at.number_input[0].set_value(190).run()  # entre la banda chica (≤186) y la mediana (≥202)
    next(b for b in at.button if b.label == "Usar mi empresa").click().run()
    assert not at.exception
    assert not at.error
    assert "no cae en ninguna banda" in textos(at)


def test_semaforo_aparece_al_mover_una_palanca(tmp_path):
    at = app_con(tmp_path, semaforo=True)
    assert "semaforo-direccion" not in textos(at)  # en el estado inicial no dibuja nada
    subir_aguinaldo(at, 5)
    assert not at.exception
    assert "semaforo-direccion" in textos(at)
    assert "semaforo-solidez" in textos(at)


@FALTA_ESCENARIOS
def test_escenarios_a_y_b_se_comparan_y_se_limpian(tmp_path):
    at = app_con(tmp_path, escenarios=True)
    subir_aguinaldo(at, 5)
    boton(at, "btn_guardar").click().run()
    assert "Escenario A guardado" in textos(at)
    boton(at, "mas_prima_vac_op").click().run()
    boton(at, "btn_guardar").click().run()
    assert not at.exception
    assert "Escenarios A y B" in textos(at)
    boton(at, "btn_guardar").click().run()  # un tercero no cabe: avisa y no truena
    assert not at.exception
    boton(at, "btn_limpiar_ab").click().run()
    assert "Escenarios A y B" not in textos(at)


@FALTA_HISTORIAL
def test_historial_guarda_cada_explicacion_y_restablecer_lo_borra(tmp_path):
    at = app_con(tmp_path, historial=True)
    subir_aguinaldo(at, 5)
    boton(at, "btn_explicar").click().run()
    boton(at, "mas_prima_vac_op").click().run()
    boton(at, "btn_explicar").click().run()
    assert not at.exception
    assert len(at.session_state["historial"]) == 2
    boton(at, "btn_restablecer").click().run()
    assert "historial" not in at.session_state
