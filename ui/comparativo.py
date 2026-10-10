import streamlit as st

NOMBRES_INDICADORES = {
    "rot_anual": "Rotación Anual",
    "rot_temprana": "Rotación Temprana",
    "ausentismo": "Ausentismo",
}


def _html(texto):
    st.markdown(texto, unsafe_allow_html=True)


def _fmt(valor):
    """Porcentaje con un decimal; guion si el dato no existe (por ejemplo, resto sin grupo)."""
    return "—" if valor is None else f"{valor:.1%}"


def render(datos):
    """Comparativo: empresa, grupo y resto en grande, con encabezado y aviso de grupo completado."""
    grupo = datos["grupo"]
    ind_resto = (datos.get("resto") or {}).get("indicadores") or {}

    # Encabezado
    _html(f'<div class="comp-encabezado">Comparando con {grupo["n"]} empresas reales</div>')

    if grupo.get("completado"):
        _html('<div class="comp-aviso">Grupo completado con empresas similares</div>')

    filas = ""
    for clave, nombre in NOMBRES_INDICADORES.items():
        emp = datos["empresa"]["indicadores"][clave]
        gru = (grupo.get("indicadores") or {}).get(clave)
        res = ind_resto.get(clave)
        # En los tres indicadores un valor menor es mejor
        clase_grupo = "cifra-grande-acento" if gru is not None and gru < emp else "cifra-grande"
        filas += (
            f'<tr><td class="nombre">{nombre}</td>'
            f'<td><span class="cifra-grande">{_fmt(emp)}</span></td>'
            f'<td><span class="{clase_grupo}">{_fmt(gru)}</span></td>'
            f'<td><span class="cifra-grande">{_fmt(res)}</span></td></tr>'
        )
    _html(
        '<table class="tabla"><tr><th></th><th>Empresa</th><th>Grupo</th><th>Resto</th></tr>'
        f"{filas}</table>"
    )