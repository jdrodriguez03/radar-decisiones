"""Pruebas del panel ⚙ y de las etiquetas. Dueño: Juanes."""
from ui.procedencia import AMBAR, ACENTO, observado, supuesto
from ui.supuestos import por_defecto


def test_valores_por_defecto():
    assert por_defecto() == {"costo_por_baja": 15000, "costo_ruta_mensual": 35000}

def test_observado_lleva_texto_y_color():
    resultado = observado("22 empresas")
    assert "22 empresas" in resultado
    assert ACENTO in resultado

def test_supuesto_escapa_html():
    resultado = supuesto("<b>")
    assert"<b>" not in resultado
    assert "&lt;b&gt;" in resultado
    assert AMBAR in resultado