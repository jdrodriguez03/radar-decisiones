import streamlit as st

EPS = 1e-9


def _moneda(v):
    return f"${v:,.2f}"


def _pct(v):
    return f"{v:.1%}"


CONTROLES = {
    "sal_dia_ini": {
        "nombre": "Salario diario inicial", "min": 250.0, "max": 380.0, "paso": 10.0,
        "fmt": _moneda, "slider": "%.0f",
    },
    "aguinaldo_op": {
        "nombre": "Aguinaldo (días)", "min": 15.0, "max": 32.0, "paso": 1.0,
        "fmt": lambda v: f"{v:.0f}", "slider": "%.0f",
    },
    "prima_vac_op": {
        "nombre": "Prima Vacacional", "min": 0.25, "max": 1.0, "paso": 0.05,
        "fmt": _pct, "slider": "%.2f",
    },
    "vales_op": {
        "nombre": "Vales", "min": 0.06, "max": 0.12, "paso": 0.005,
        "fmt": _pct, "slider": "%.3f",
    },
    "rutas_x100": {
        "nombre": "Rutas por 100", "min": 0.0, "max": 10.8, "paso": 0.5,
        "fmt": lambda v: f"{v:.2f}", "slider": "%.1f",
    },
}


def _k(clave):
    return f"valor_{clave}"


def _rango(cfg, real):
    """Mismo paso, pero con la cuadrícula anclada al valor real (así el slider no lo ajusta)."""
    p = cfg["paso"]
    n_abajo = int((real - cfg["min"] + EPS) // p)
    n_arriba = int((cfg["max"] - real + EPS) // p)
    return round(real - n_abajo * p, 6), round(real + n_arriba * p, 6)


def _iniciar(perfil):
    """Al cambiar de empresa, todo vuelve a los valores reales."""
    if st.session_state.get("_empresa_id") != perfil["id"]:
        reales = {c: float(perfil["palancas"][c]) for c in CONTROLES}
        st.session_state["_reales"] = reales
        st.session_state["_rangos"] = {c: _rango(CONTROLES[c], v) for c, v in reales.items()}
        st.session_state["_previos"] = dict(reales)
        st.session_state["cambio"] = None
        for c, v in reales.items():
            st.session_state[_k(c)] = v
        st.session_state["_empresa_id"] = perfil["id"]


def _registrar(clave):
    """Guarda la última palanca movida: valor de (anterior) y a (nuevo)."""
    de = st.session_state["_previos"][clave]
    a = st.session_state[_k(clave)]
    if abs(a - de) > EPS:
        st.session_state["cambio"] = {"palanca": clave, "de": de, "a": a}
    st.session_state["_previos"][clave] = a


def _paso(clave, signo):
    cfg = CONTROLES[clave]
    lo, hi = st.session_state["_rangos"][clave]
    nuevo = st.session_state[_k(clave)] + signo * cfg["paso"]
    st.session_state[_k(clave)] = round(min(max(nuevo, lo), hi), 6)
    _registrar(clave)


def _restablecer():
    reales = st.session_state["_reales"]
    for c, v in reales.items():
        st.session_state[_k(c)] = v
    st.session_state["_previos"] = dict(reales)
    st.session_state["cambio"] = None


def render(perfil):
    """Dibuja los controles y devuelve (palancas_movidas, cambio)."""
    _iniciar(perfil)

    for clave, cfg in CONTROLES.items():
        lo, hi = st.session_state["_rangos"][clave]
        c_nom, c_val = st.columns([3, 2], gap="small", vertical_alignment="center")
        c_nom.markdown(f'<div class="palanca-nombre">{cfg["nombre"]}</div>', unsafe_allow_html=True)
        c_val.markdown(
            f'<div class="palanca-valor">{cfg["fmt"](st.session_state[_k(clave)])}</div>',
            unsafe_allow_html=True,
        )
        c_menos, c_mas, c_slider = st.columns([1.3, 1.3, 5], gap="small", vertical_alignment="center")
        c_menos.button("−", key=f"menos_{clave}", on_click=_paso, args=(clave, -1),
                       help=f"Bajar {cfg['paso']:g}", use_container_width=True)
        c_mas.button("+", key=f"mas_{clave}", on_click=_paso, args=(clave, 1),
                     help=f"Subir {cfg['paso']:g}", use_container_width=True)
        c_slider.slider(
            cfg["nombre"], min_value=lo, max_value=hi, step=cfg["paso"],
            format=cfg["slider"], key=_k(clave), label_visibility="collapsed",
            on_change=_registrar, args=(clave,),
        )

    st.button("↻ Restablecer", on_click=_restablecer)

    reales = st.session_state["_reales"]
    palancas_movidas = {
        c: st.session_state[_k(c)]
        for c in CONTROLES
        if abs(st.session_state[_k(c)] - reales[c]) > EPS
    }
    return palancas_movidas, st.session_state["cambio"]