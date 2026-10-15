"""Rutas y constantes compartidas. Todos importan de aquí; nadie escribe rutas a mano."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

# Datos
RUTA_XLSX = RAIZ / "data" / "raw" / "BASE_REDUCIDA_v2.xlsx"
RUTA_EMPRESAS = RAIZ / "data" / "processed" / "empresas.parquet"
RUTA_SUPUESTOS = RAIZ / "data" / "processed" / "supuestos.json"
RUTA_CACHE = RAIZ / "data" / "processed" / "cache.json"
RUTA_EJEMPLO = RAIZ / "contrato" / "ejemplo.json"
RUTA_FIXTURES = RAIZ / "contrato" / "fixtures"

# Palancas: columna -> (minimo, maximo, paso)
PALANCAS = {
    "sal_dia_ini": (250, 380, 10),
    "aguinaldo_op": (15, 32, 1),
    "prima_vac_op": (0.25, 1.00, 0.05),
    "vales_op": (0.06, 0.12, 0.005),
    "rutas_x100": (0, 10.8, 0.5),
}

# Indicadores
INDICADORES = ["rot_anual", "bajas_menos3m", "aus_inj_op"]

# Escala del cuestionario para motivos de baja
ESCALA_MOTIVOS = {0: 0.0, 1: 0.10, 2: 0.30, 3: 0.50, 4: 0.70, 5: 1.00}

# Reglas del motor
MIN_GRUPO = 5
UMBRAL_SENAL_CLARA = 0.05
UMBRAL_SENAL_DEBIL = 0.15

# Supuestos por defecto
COSTO_POR_BAJA = 15000

# IA
MODELO_IA = "claude-sonnet-5-5"
TEMPERATURA_IA = 0.3  # baja: textos más parecidos entre sí y más fieles a la forma pedida
TIEMPO_LIMITE_IA_SEG = 4  # si la primera palabra no llega en este tiempo, sale la plantilla
TIEMPO_TOTAL_IA_SEG = 8  # si el texto completo no llega en este tiempo, sale la plantilla
PAUSA_ESCRITURA_SEG = 0.03  # el efecto de escritura: una palabra cada 30 ms (unos 2 s para 70 palabras)
