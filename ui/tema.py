"""Colores y estilos. Dueño: Gaby."""
import streamlit as st

# Tema oscuro (config.toml) aplicado a la estructura de la plantilla
FONDO = "#0B0F14"      # fondo casi negro
SUPERFICIE = "#132217" # pastillas, encabezado de tabla, triángulo oscuro
TRIANGULO = "#1E5A4A"  # triángulo secundario
LINEA = "#2A4A3A"      # líneas de la tabla
TEXTO = "#D8DDE3"      # texto principal
ACENTO = "#46D3AA"     # único color de resalte: títulos y cifra del grupo
GRIS = "#8B949E"       # textos secundarios
AMBAR = "#D29922"      # para valores supuestos

# Tamaños de letra (pensados para proyector)
TAM_CIFRA = "40px"
TAM_TITULO = "44px"
TAM_TEXTO = "18px"


def aplicar_estilos():
    """Fuentes, colores, decoración y tamaños de la plantilla."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@800&family=Oswald:wght@500&family=Nunito:ital,wght@0,400;0,600;1,400&display=swap');

        html, body, [class*="st-"], .stApp {{ font-family: 'Nunito', sans-serif; color: {TEXTO}; }}
        .stApp {{ background: {FONDO}; }}
        header[data-testid="stHeader"] {{ display: none; }}
        .block-container {{ padding-top: 1.2rem; padding-bottom: 0.5rem; max-width: 1500px; }}
        footer, [data-testid="stFooter"], [data-testid="stBottom"] {{ display: none; }}
        [data-testid="stMain"] > div:last-child, [data-testid="stAppViewContainer"] {{ padding-bottom: 0; }}
        [data-testid="stVerticalBlock"] > div:last-child {{ margin-bottom: 0; }}

        /* triángulos de la esquina superior derecha */
        .tri-1 {{ position: fixed; top: 0; right: 0; width: 600px; height: 70px;
                  background: {SUPERFICIE}; clip-path: polygon(12% 0, 100% 0, 100% 100%, 0 100%); z-index: 0; }}
        .tri-2 {{ position: fixed; top: 70px; right: 0; width: 140px; height: 190px;
                  background: {TRIANGULO}; clip-path: polygon(0 0, 100% 0, 100% 100%); z-index: 0; }}
        [data-testid="stMain"] {{ position: relative; z-index: 1; }}

        .titulo-app {{ font-family: 'Poppins', sans-serif; font-weight: 800; font-size: 54px;
                       color: {ACENTO}; line-height: 1; text-transform: uppercase; }}
        .subtitulo {{ font-size: 15px; color: {GRIS}; text-transform: uppercase; margin: 4px 0 28px 8px; }}
        .titulo-col {{ font-family: 'Oswald', sans-serif; font-weight: 500; font-size: {TAM_TITULO};
                       letter-spacing: 6px; text-transform: uppercase; color: {TEXTO};
                       text-align: center; margin-bottom: 28px; }}

        /* palancas */
        div[data-testid="stTextInput"] label p {{ font-size: 26px; color: {TEXTO}; margin-bottom: 0; }}
        div[data-testid="stTextInput"] div[data-baseweb="input"] {{ background: {SUPERFICIE}; border-radius: 16px; border: 1px solid {LINEA}; }}
        div[data-testid="stTextInput"] input {{ background: transparent; height: 34px; font-style: italic;
                       letter-spacing: 2px; color: {ACENTO}; -webkit-text-fill-color: {ACENTO}; }}
        .stButton button {{ background: {SUPERFICIE}; border: 1px solid {LINEA}; border-radius: 16px;
                       color: {TEXTO}; font-style: italic; width: 100%; }}
        .stButton button:hover {{ border-color: {ACENTO}; color: {ACENTO}; }}

        .palanca-nombre {{ font-size: 22px; color: {TEXTO}; padding-top: 6px; }}
        .palanca-valor {{ font-size: 22px; font-style: italic; color: {ACENTO}; padding-top: 6px; }}

        /* tabla de indicadores */
        .tabla {{ width: 100%; border-collapse: collapse; border: 3px solid {LINEA}; }}
        .tabla th {{ background: {SUPERFICIE}; color: {TEXTO}; font-size: 22px; font-weight: 700;
                     padding: 14px 6px; text-align: center; border: 2px solid {LINEA}; }}
        .tabla td {{ font-size: {TAM_TEXTO}; color: {TEXTO}; text-align: center; padding: 16px 8px;
                     border: 2px solid {LINEA}; background: {FONDO}; }}
        .tabla td.nombre {{ font-size: 20px; }}
        .cifra {{ font-size: 24px; font-weight: 700; color: {TEXTO}; }}
        .cifra-acento {{ font-size: 24px; font-weight: 700; color: {ACENTO}; }}
        .supuesto {{ color: {AMBAR}; }}

        /* cifras en pesos */
        .peso {{ font-size: {TAM_CIFRA}; font-style: italic; letter-spacing: 3px; color: {TEXTO}; text-align: center; }}
        .peso-etiqueta {{ font-size: {TAM_TEXTO}; color: {GRIS}; text-align: center; }}
        .grafica {{ background: {FONDO}; border: 10px solid {SUPERFICIE}; height: 300px;
                    display: flex; align-items: center; justify-content: center; }}

        /* explicación */
        .explicacion {{ font-size: 16px; color: {TEXTO}; text-align: center; line-height: 1.5; }}
        .texto-gris {{ font-size: 15px; color: {GRIS}; text-align: center; }}
        </style>
        <div class="tri-1"></div><div class="tri-2"></div>
        """,
        unsafe_allow_html=True,
    )