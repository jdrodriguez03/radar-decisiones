# Reglas del proyecto para asistentes de código

- Proyecto: Radar de Decisiones (Streamlit). El motor compara empresas reales; la IA solo explica. No hay modelos predictivos.
- Estructura y dueños: ver `.github/CODEOWNERS`. Solo editar archivos de tu dueño.
- Las firmas de las funciones públicas están congeladas. No cambiarlas.
- El contrato JSON está en `contrato/ejemplo.json`. Toda salida del motor debe validar contra `contrato/modelo.py`.
- Rutas y constantes: siempre desde `config.py`.
- La IA nunca inventa cifras: todo número del texto debe estar en el JSON.
- Lenguaje: "las empresas que ya hacen esto muestran", nunca "logrará" ni "reducirá".
- Nunca subir `.streamlit/secrets.toml` ni `data/raw/*.xlsx`.
