"""Pruebas de scripts/revisar_cache.py, sin internet. Dueño: Julian."""
import pytest

from ia.cache import cargar
from motor.datos import cargar as cargar_empresas
from scripts import generar_cache as gc
from scripts import revisar_cache as rc
from tests.test_generar_cache import SUPUESTOS, ClienteEco


@pytest.fixture(autouse=True)
def rutas_temporales(monkeypatch, tmp_path):
    """Ni el caché real ni docs/revision_cache.md se tocan."""
    monkeypatch.setattr("config.RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setattr("config.PAUSA_ESCRITURA_SEG", 0)
    monkeypatch.setattr(rc, "RUTA_REPORTE", tmp_path / "revision_cache.md")


@pytest.fixture(scope="module")
def secuencias():
    return gc.armar_secuencias(gc.cargar_casos(), cargar_empresas(), SUPUESTOS)


def test_con_el_cache_lleno_todo_sale_del_cache(secuencias):
    gc.generar(secuencias, cliente=ClienteEco(secuencias))
    filas, sobrantes = rc.revisar_todo(secuencias, cargar())
    assert len(filas) == 26
    assert {f["fuente"] for f in filas} == {"cache"}
    assert sobrantes == []
    assert all(f["segundos"] < rc.LIMITE_GUION_SEG for f in filas if f["guion"])


def test_con_el_cache_vacio_sale_la_plantilla_y_se_marca(secuencias):
    filas, _ = rc.revisar_todo(secuencias, {})
    assert {f["fuente"] for f in filas} == {"plantilla"}
    assert all("no del caché" in rc.problemas(f)[0] for f in filas)


def test_las_llaves_que_nadie_usa_se_listan(secuencias):
    _, sobrantes = rc.revisar_todo(secuencias, {"COMPAÑIA 99|vieja|15000": {"texto": "x"}})
    assert sobrantes == ["COMPAÑIA 99|vieja|15000"]


def test_el_reporte_trae_tabla_y_textos(secuencias):
    gc.generar(secuencias, cliente=ClienteEco(secuencias))
    filas, sobrantes = rc.revisar_todo(secuencias, cargar())
    reporte = rc.a_markdown(filas, sobrantes)
    assert "| # | Guion |" in reporte
    assert "## Textos" in reporte
    assert "COMPAÑIA 15|sal_dia_ini=340|15000" in reporte
