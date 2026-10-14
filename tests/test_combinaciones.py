"""Revisa que combinaciones.yaml esté completo y bien escrito. Dueño: Juanes."""
import pytest

from scripts.correr_combinaciones import cargar_casos, pesos, validar_caso


def test_son_20_casos_con_id_unico():
    casos = cargar_casos()
    assert len(casos) == 20
    assert len({c["id"] for c in casos}) == 20


def test_estan_los_tres_pasos_del_guion():
    guion = [c for c in cargar_casos() if c["tipo"] == "guion"]
    assert [c["id"] for c in guion] == ["G1", "G2", "G3"]


def test_palanca_inexistente_falla():
    with pytest.raises(ValueError):
        validar_caso({"id": "X", "empresa": "COMPAÑIA 36", "palancas": {"bono": 1}})


def test_valor_fuera_de_rango_falla():
    with pytest.raises(ValueError):
        validar_caso({"id": "X", "empresa": "COMPAÑIA 36", "palancas": {"aguinaldo_op": 50}})


def test_formato_pesos():
    assert pesos(6341580) == "$6.3 M"
    assert pesos(-5_100_000) == "−$5.1 M"