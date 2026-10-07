"""Pruebas para motor/datos.py."""
from config import PALANCAS
from motor.datos import cargar

#Se verifica que la función cargar devuelva un DataFrame con 40 empresas únicas 
# y que contenga todas las columnas de palancas definidas en config.PALANCAS.
def test_cargar_devuelve_40_empresas_con_las_palancas():
    empresas = cargar()

    assert len(empresas) == 40
    assert empresas["empresa"].nunique() == 40
    assert set(PALANCAS).issubset(empresas.columns)
