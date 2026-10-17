import time

import streamlit as st

EPS = 1e-9
DEPURAR = False  # True: imprime en la terminal lo que hacen los botones (para buscar fallas)


def _log(texto):
    if DEPURAR:
        eventos = st.session_state.setdefault("_eventos", [])
        eventos.append(texto)
        del eventos[:-8]  # solo los últimos 8
        print(f"[controles] {texto}", flush=True)


def _moneda(v):
    return f"${v:,.2f}"


def _pct(v):
    return f"{v:.1%}"


# Rangos y pasos de la tabla de controles del proyecto.
# prima y vales se guardan como fracción (0.25 = 25%), igual que el contrato.
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
    """Mismo paso, con la cuadrícula anclada al valor real y un rango que siempre lo incluye.

    Si el valor real queda fuera del rango de la tabla (por ejemplo 15.46 rutas con máximo 10.8),
    el rango se extiende hasta ese valor para que el slider no falle.
    """
    p = cfg["paso"]
    piso, techo = min(cfg["min"], real), max(cfg["max"], real)
    n_abajo = int((real - piso + EPS) // p)
    n_arriba = int((techo - real + EPS) // p)
    lo, hi = round(real - n_abajo * p, 6), round(real + n_arriba * p, 6)
    if hi <= lo:  # el slider necesita un mínimo menor que el máximo
        hi = round(lo + p, 6)
    return lo, hi


def _falta(valor):
    """True si la palanca no tiene dato (None o NaN), como pasa con algunas empresas de la encuesta."""
    return valor is None or valor != valor


def _iniciar(perfil):
    """Al cambiar de empresa (o de valores capturados), todo vuelve a los valores reales."""
    palancas = perfil["palancas"]
    firma = (perfil["id"], str(sorted((c, palancas.get(c)) for c in CONTROLES)))
    if st.session_state.get("_firma_perfil") != firma:
        reales = {c: float(palancas[c]) for c in CONTROLES if not _falta(palancas.get(c))}
        st.session_state["_reales"] = reales
        st.session_state["_sin_dato"] = [c for c in CONTROLES if c not in reales]
        st.session_state["_rangos"] = {c: _rango(CONTROLES[c], v) for c, v in reales.items()}
        st.session_state["_previos"] = dict(reales)
        st.session_state["cambio"] = None
        for c, v in reales.items():
            st.session_state[_k(c)] = v
        st.session_state["_firma_perfil"] = firma
        st.session_state.pop("estado_explicado", None)  # otra empresa: no hay última explicación
    # Streamlit borra el valor de un slider cuando una ejecución no lo dibuja (por ejemplo, al ver «Mi empresa»
    # sin enviar). Si pasó, se restaura con el último valor conocido en lugar de fallar.
    for clave, real in st.session_state["_reales"].items():
        if _k(clave) not in st.session_state:
            st.session_state[_k(clave)] = st.session_state["_previos"].get(clave, real)


def _marcar_click():
    """Guarda el instante del clic; el panel lo usa para medir cuánto tarda en redibujar."""
    st.session_state["_t_click"] = time.perf_counter()


def _registrar(clave):
    """Guarda la última palanca movida: valor de (anterior) y a (nuevo)."""
    _marcar_click()
    de = st.session_state["_previos"][clave]
    a = st.session_state[_k(clave)]
    if abs(a - de) > EPS:
        st.session_state["cambio"] = {"palanca": clave, "de": de, "a": a}
    st.session_state["_previos"][clave] = a


def _paso(clave, signo):
    _marcar_click()
    cfg = CONTROLES[clave]
    lo, hi = st.session_state["_rangos"][clave]
    nuevo = st.session_state[_k(clave)] + signo * cfg["paso"]
    st.session_state[_k(clave)] = round(min(max(nuevo, lo), hi), 6)
    _log(f"_paso {clave} {signo:+d} -> {st.session_state[_k(clave)]}")
    _registrar(clave)


def _restablecer():
    _marcar_click()
    reales = st.session_state["_reales"]
    _log(f"_restablecer: valores reales {reales}")
    for c, v in reales.items():
        st.session_state[_k(c)] = v
    st.session_state["_previos"] = dict(reales)
    st.session_state["cambio"] = None
    st.session_state.pop("estado_explicado", None)  # restablecer también borra la última explicación


def render(perfil, con_guardar=False):
    """Dibuja los controles y devuelve (palancas_movidas, cambio).

    Con con_guardar=True pone «Guardar escenario» junto a Restablecer y devuelve un tercer valor:
    True en la ejecución en que se pulsó.
    """
    _iniciar(perfil)

    # Los botones quedan debajo de las palancas, pero se leen primero: así Restablecer cambia los valores
    # antes de que se dibujen los sliders de esta ejecución (sin depender de un callback).
    zona_filas = st.container()
    zona_botones = st.container()
    guardar = False
    with zona_botones:
        # Misma estructura con o sin «Guardar»: en las pruebas, el botón suelto fallaba y este esquema no
        c_rest, c_guardar = st.columns(2, gap="small")
        reiniciar = c_rest.button("↻ Restablecer", key="btn_restablecer", use_container_width=True)
        if con_guardar:
            guardar = c_guardar.button("Guardar escenario", key="btn_guardar", use_container_width=True)
    if reiniciar:
        _restablecer()
    _log(f"render: reiniciar={reiniciar} guardar={guardar}")

    with zona_filas:
        for clave, cfg in CONTROLES.items():
            if clave in st.session_state["_sin_dato"]:
                c_nom, c_val = st.columns([3, 2], gap="small", vertical_alignment="center")
                c_nom.markdown(f'<div class="palanca-nombre">{cfg["nombre"]}</div>', unsafe_allow_html=True)
                c_val.markdown('<div class="palanca-valor">Sin dato</div>', unsafe_allow_html=True)
                continue
            lo, hi = st.session_state["_rangos"][clave]
            c_nom, c_val = st.columns([3, 2], gap="small", vertical_alignment="center")
            c_nom.markdown(f'<div class="palanca-nombre">{cfg["nombre"]}</div>', unsafe_allow_html=True)
            c_val.markdown(
                f'<div class="palanca-valor">{cfg["fmt"](st.session_state[_k(clave)])}</div>',
                unsafe_allow_html=True,
            )
            c_menos, c_mas, c_slider = st.columns([1.3, 1.3, 5], gap="small", vertical_alignment="center")
            c_menos.button("−", key=f"menos_{clave}", on_click=_paso, args=(clave, -1), use_container_width=True)
            c_mas.button("+", key=f"mas_{clave}", on_click=_paso, args=(clave, 1), use_container_width=True)
            c_slider.slider(
                cfg["nombre"], min_value=lo, max_value=hi, step=cfg["paso"],
                format=cfg["slider"], key=_k(clave), label_visibility="collapsed",
                on_change=_registrar, args=(clave,),
            )
            real = st.session_state["_reales"][clave]
            if real < cfg["min"] - EPS or real > cfg["max"] + EPS:
                st.markdown(
                    f'<div class="palanca-aviso">Su valor ({cfg["fmt"](real)}) está fuera del rango de la encuesta '
                    f'({cfg["fmt"](cfg["min"])} a {cfg["fmt"](cfg["max"])}).</div>',
                    unsafe_allow_html=True,
                )

    if DEPURAR:  # panel de ayuda: muestra en pantalla qué ejecuciones y clics llegaron
        st.session_state["_corridas"] = st.session_state.get("_corridas", 0) + 1
        st.code(f"ejecución {st.session_state['_corridas']}\n" + "\n".join(st.session_state.get("_eventos", [])))

    reales = st.session_state["_reales"]
    palancas_movidas = {
        c: st.session_state[_k(c)]
        for c in reales
        if abs(st.session_state[_k(c)] - reales[c]) > EPS
    }
    if con_guardar:
        return palancas_movidas, st.session_state["cambio"], guardar
    return palancas_movidas, st.session_state["cambio"]