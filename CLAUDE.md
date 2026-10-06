# Reglas del proyecto para asistentes de código

Proyecto: Radar de Decisiones (Streamlit). El motor compara empresas reales; la IA solo explica. No hay modelos predictivos.

## Estructura
- `motor/` calcula. No importa streamlit, ia ni ui.
- `ia/` explica. No calcula empresas.
- `ui/` dibuja. No tiene fórmulas de negocio.
- `contrato/` define el JSON; `contrato/fixtures/` tiene 5 ejemplos para probar.
- `data/raw/` (el xlsx, no se sube) y `data/processed/` (parquet, supuestos y caché).
- `scripts/` tareas de una vez; `sandbox/` mini-apps; `tests/` pruebas; `docs/` documentos.
- Se corre siempre desde la raíz del repositorio.

## Reglas
- Dueños por archivo: ver `.github/CODEOWNERS`. Solo editar archivos del dueño.
- Las firmas de las funciones públicas están congeladas. No cambiarlas.
- Toda salida del motor debe validar contra `contrato/modelo.py`.
- Rutas y constantes siempre desde `config.py`.
- La IA nunca inventa cifras: todo número del texto debe estar en el JSON.
- Lenguaje: "las empresas que ya hacen esto muestran", nunca "logrará" ni "reducirá".
- Nunca subir `.streamlit/secrets.toml` ni `data/raw/*.xlsx`.
- Commits: `área: qué hiciste` (motor:, ia:, ui:, docs:, fix:).
