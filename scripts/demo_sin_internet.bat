@echo off
REM Radar de Decisiones en MODO_DEMO: la app nunca llama a la API (solo caché o plantilla).
REM Se usa si el wifi de la sala falla o la API va lenta. Dueño: Julian.
REM Uso: doble clic en este archivo. Para cerrar la app, Ctrl+C en la ventana negra.

cd /d "%~dp0.."
set MODO_DEMO=1
call .venv\Scripts\activate.bat
echo.
echo   MODO_DEMO encendido: las explicaciones salen del cache o de la plantilla, sin internet.
echo.
streamlit run app.py
pause
