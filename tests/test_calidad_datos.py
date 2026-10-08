"""Pruebas para scripts/generar_calidad_datos.py."""
import pandas as pd

from scripts.generar_calidad_datos import generar_informe


#Se verifica que el informe de calidad de datos compare las palancas 
# y distinga el mínimo legal.
def test_informe_compara_palancas_y_distingue_el_minimo_legal():
    empresas = pd.DataFrame(
        {
            "empresa": ["COMPAÑIA 1", "COMPAÑIA 2"],
            "sal_dia_ini": [240.0, 300.0],
            "aguinaldo_op": [15.0, 20.0],
            "prima_vac_op": [0.25, 0.5],
            "vales_op": [0.06, 0.1],
            "rutas_x100": [0.0, 2.0],
        }
    )

    informe = generar_informe(empresas)

    assert "Valores faltantes por columna" in informe
    assert "| `sal_dia_ini` | 2 |" in informe
    assert "COMPAÑIA 1" in informe
    assert "no determina por sí solo incumplimiento del salario mínimo legal" in informe
