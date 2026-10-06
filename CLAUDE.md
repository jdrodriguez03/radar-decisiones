# Reglas del proyecto para asistentes de código

## Qué es esto
Radar de Decisiones: app Streamlit para una convocatoria corporativa (Catch). Un directivo mueve 5 palancas de compensación (sal_dia_ini, aguinaldo_op, prima_vac_op, vales_op, rutas_x100); el motor compara contra 40 empresas reales y anónimas y la IA explica el cambio en 3 frases. No hay modelos predictivos: solo comparación. La demo en vivo es el día 16. Detalle en docs/proyecto.docx; rangos y constantes en config.py.

## Cómo se corre
Siempre desde la raíz del repositorio, con Python 3.12 y el entorno .venv activo.
- streamlit run app.py
- pytest y ruff check . (el CI corre ambos en cada PR)

## De dónde salen los datos
BASE_HISTORICA.xlsx -> scripts/historica_a_reducida.py -> BASE_REDUCIDA_v2.xlsx -> scripts/preparar_datos.py -> data/processed/empresas.parquet.
Nunca editar la v2 a mano: si cambia una regla, se cambia el script (con --comparar se verifica que reproduce la v2).

## Estructura
- motor/ calcula. No importa streamlit, ia ni ui.
- ia/ explica. No calcula empresas.
- ui/ dibuja. No tiene fórmulas de negocio.
- contrato/ define el JSON (referencia: contrato/ejemplo.json); contrato/fixtures/ guardará 5 ejemplos para probar (por ahora vacía).
- data/raw/ (las dos bases en Excel; el repo es privado y los datos vienen anonimizados) y data/processed/ (parquet, supuestos y caché).
- scripts/ tareas de una vez; sandbox/ mini-apps; tests/ pruebas; docs/ documentos.

## Reglas
- Dueños por archivo: ver .github/CODEOWNERS. Solo editar archivos del dueño.
- Las firmas de las funciones públicas están congeladas. Los archivos con raise NotImplementedError son esqueleto: se llenan sin cambiar la firma.
- Toda salida del motor debe validar contra contrato/modelo.py.
- Rutas y constantes siempre desde config.py.
- La IA nunca inventa cifras: todo número del texto debe estar en el JSON.
- Lenguaje: "las empresas que ya hacen esto muestran", nunca "logrará" ni "reducirá".
- Nunca subir .streamlit/secrets.toml. En data/raw/ solo van las dos bases anonimizadas; ningún otro Excel.

## Git
- No se sube directo a main: una rama por persona y bloque (a/e2-motor = letra del dueño y bloque-tema), PR a main, revisión conjunta cada dos días con las aprobaciones de los demás y el CI en verde.
- Commits: "área: qué hiciste", en presente (motor:, ia:, ui:, data:, scripts:, tests:, docs:, chore:, fix:).

## Con quién se trabaja
Los cuatro integrantes (Aleja, Gaby, Julian, Juanes) no son expertos en git. Explicar en español, en simple y con el porqué de cada paso.
