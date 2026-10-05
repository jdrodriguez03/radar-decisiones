# Radar de Decisiones

Herramienta donde un directivo mueve una decisión de compensación y ve qué les pasa a las empresas reales que ya la tomaron. No predice: compara contra 40 empresas de la encuesta.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate        # Windows (Git Bash): source .venv/Scripts/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # y poner la llave real
```

## Datos
Copiar `BASE_REDUCIDA_v2.xlsx` desde la carpeta del equipo a `data/raw/` (no se sube a git). Luego: `make datos`.

## Comandos
- `make run`: abre la app
- `make test`: corre las pruebas
- `make lint`: revisa el estilo
