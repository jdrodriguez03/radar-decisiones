"""Prueba manual de la API del motor al mover el aguinaldo."""

import json
import time

import streamlit as st

from config import RUTA_SUPUESTOS
from motor.api import calcular_estado
from motor.datos import cargar
from ui.selector import perfil_demo


# Función principal que ejecuta la prueba manual de la API del motor al mover el aguinaldo.
def main():
    st.title("Sandbox del motor")
    empresas = cargar()
    perfil = perfil_demo(empresas, "COMPAÑIA 36")
    aguinaldo_base = perfil["palancas"]["aguinaldo_op"]
    aguinaldo = st.slider(
        "Aguinaldo (días)",
        min_value=15,
        max_value=32,
        value=int(aguinaldo_base),
        step=1,
    )

    palancas_movidas = (
        {} if aguinaldo == aguinaldo_base else {"aguinaldo_op": float(aguinaldo)}
    )
    cambio = (
        None
        if not palancas_movidas
        else {
            "palanca": "aguinaldo_op",
            "de": float(aguinaldo_base),
            "a": float(aguinaldo),
        }
    )
    supuestos = json.loads(RUTA_SUPUESTOS.read_text(encoding="utf-8"))

    inicio = time.perf_counter()
    estado = calcular_estado(
        empresas,
        perfil,
        palancas_movidas,
        cambio,
        supuestos,
    )
    milisegundos = (time.perf_counter() - inicio) * 1000

    st.caption(f"Tiempo de respuesta: {milisegundos:.2f} ms (objetivo: menos de 50 ms)")
    st.json(estado)

# Se ejecuta la función principal si el script se ejecuta directamente.
if __name__ == "__main__":
    main()
