"""Pruebas para scripts/preparar_datos.py."""
#Se verifica que la función preparar_datos devuelva un 
# DataFrame con 40 empresas únicas y que la rotación anual 
# esté entre 0 y 3, con una mediana aproximada de 0.372.
import pytest

from scripts.preparar_datos import preparar_datos


def test_preparar_datos_devuelve_40_empresas_unicas():
    empresas = preparar_datos()

    assert len(empresas) == 40
    assert empresas["empresa"].nunique() == 40


def test_rotacion_anual_esta_entre_cero_y_tres():
    empresas = preparar_datos()

    assert empresas["rot_anual"].between(0, 3).all()
    assert empresas["rot_anual"].median() == pytest.approx(0.372)
