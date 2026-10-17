"""Prueba mínima de botones, para saber si el problema es de Streamlit, del navegador o del proyecto.

Uso:  streamlit run sandbox/b_botones.py
Haz clic en cada botón y anota cuáles responden.
"""

import streamlit as st

st.set_page_config(layout="wide")
st.session_state.setdefault("n", 0)


def sumar():
    st.session_state["n"] += 1


def mas(clave):
    st.session_state[clave] = min(st.session_state[clave] + 5, 100)


def pruebas(sufijo):
    st.button("A: botón simple con callback", on_click=sumar, key="a" + sufijo)
    st.write("Veces pulsado A (compartido):", st.session_state["n"])

    clave = "v" + sufijo
    st.session_state.setdefault(clave, 10)
    st.button("B: + (cambia el slider)", on_click=mas, args=(clave,), key="b" + sufijo)
    st.slider("valor", 0, 100, key=clave)

    with st.form("f" + sufijo):
        x = st.number_input("número", value=1, key="x" + sufijo)
        enviado = st.form_submit_button("C: enviar formulario")
    if enviado:
        st.success(f"Formulario enviado con {x}")


izq, der = st.columns(2)
with izq:
    st.subheader("Sin fragmento")
    pruebas("")
with der:
    st.subheader("Dentro de st.fragment")

    @st.fragment
    def con_fragmento():
        pruebas("_f")

    con_fragmento()