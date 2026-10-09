import copy
import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from ui.controles import render
from ui.tema import aplicar_estilos

st.set_page_config(layout="wide")
aplicar_estilos()

ruta = Path(__file__).resolve().parents[1] / "contrato" / "ejemplo.json"
datos = json.loads(ruta.read_text(encoding="utf-8"))

otra = copy.deepcopy(datos["empresa"])
otra["id"] = "Compañía 12 (prueba)"
otra["palancas"].update(sal_dia_ini=280.0, aguinaldo_op=20, prima_vac_op=0.5)
empresas = {datos["empresa"]["id"]: datos["empresa"], otra["id"]: otra}

elegida = st.selectbox("Empresa", list(empresas))
palancas_movidas, cambio = render(empresas[elegida])

st.write("palancas_movidas")
st.json(palancas_movidas)
st.write("cambio")
st.json(cambio)