# Radar de Decisiones

> ## ⚠️ Antes de tocar nada, lee la guía rápida
> **[`docs/00_LEER_PRIMERO_guia_rapida_del_repositorio.docx`](docs/00_LEER_PRIMERO_guia_rapida_del_repositorio.docx)**: cómo está organizado el repositorio, cómo arrancar en VS Code, cómo se hacen los commits y cómo se revisa y se sube el trabajo. Es obligatoria para los cuatro y hay que leerla completa, con calma.

Herramienta donde un directivo mueve una decisión de compensación y ve qué les pasa a las empresas reales que ya la tomaron. **No predice**: compara contra 40 empresas anónimas de la encuesta, y una IA explica el resultado en 3 frases.

Proyecto del equipo para la convocatoria Catch. La demo en vivo es el día 16.

## Cómo funciona

1. El directivo mueve una o más de las **5 palancas**: salario diario inicial, aguinaldo, prima vacacional, vales de despensa y rutas de transporte.
2. El **motor** (`motor/`) busca las empresas que ya están en ese nivel y las compara con el resto en rotación anual, bajas en menos de 3 meses y ausentismo injustificado.
3. La **IA** (`ia/`) explica la diferencia en 3 frases, usando solo cifras que están en el resultado. Si tarda más de 4 segundos, se muestra un texto de respaldo.
4. La **pantalla** (`app.py` y `ui/`) muestra todo en Streamlit.

El motor entrega un JSON con una forma fija (ver `contrato/ejemplo.json`); ese acuerdo permite que cada persona trabaje su pieza sin esperar a las demás.

## Instalación

Necesitas Python 3.12 y git. Desde la carpeta del repositorio:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows (Git Bash): source .venv/Scripts/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # y poner la llave real
```

La llave de la API va solo en `.streamlit/secrets.toml`, que git ignora. Nunca se sube.

## Cómo se corre

Siempre desde la raíz del repositorio, con el entorno `.venv` activo:

| Comando | Qué hace |
| --- | --- |
| `streamlit run app.py` | Abre la app |
| `pytest` | Corre las pruebas |
| `ruff check .` | Revisa el estilo |

`pytest` y `ruff check .` también corren solos en cada PR (CI). Si salen en rojo, el PR no se puede aprobar.

## Los datos

```
BASE_HISTORICA.xlsx → scripts/historica_a_reducida.py → BASE_REDUCIDA_v2.xlsx
                    → scripts/preparar_datos.py → data/processed/empresas.parquet → la app
```

- Las dos bases en Excel viven en `data/raw/` y vienen anonimizadas. El repositorio es privado.
- La v2 no se edita a mano: si cambia una regla, se cambia el script. Para comprobar que lo reproduce: `python scripts/historica_a_reducida.py --comparar data/raw/BASE_REDUCIDA_v2.xlsx`.
- Qué se escogió de la histórica y cómo se codificó cada columna: [`docs/diccionario_reduccion.md`](docs/diccionario_reduccion.md).
- Para regenerar los datos de la app: `python scripts/preparar_datos.py`.

## Estructura

| Carpeta | Qué hay |
| --- | --- |
| `motor/` | Cálculo: carga datos, compara grupos, arma el JSON, costos |
| `ia/` | Prompts, llamada al modelo, texto de respaldo y validación de cifras |
| `ui/` | Una pieza de pantalla por archivo |
| `contrato/` | La forma del JSON, un ejemplo y los casos de prueba |
| `data/` | `raw/` con las bases en Excel; `processed/` con parquet, supuestos y caché |
| `scripts/` | Tareas que se corren una vez (preparar datos, generar caché, verificar la demo) |
| `sandbox/` | Mini-apps para probar tu pieza sola |
| `tests/` | Pruebas automáticas |
| `docs/` | Documentos del proyecto |
| `.github/` | CI, dueños de cada archivo y plantilla de PR |

`config.py` en la raíz guarda las rutas, los rangos de las palancas y los umbrales del motor. Todo el código importa de ahí; nadie escribe rutas a mano.

## Cómo trabajamos

- **No se sube directo a `main`.** Cada persona trabaja en su rama (`a/e2-motor`: letra del dueño, bloque y tema) y abre un PR.
- **Revisión conjunta cada dos días**: el equipo revisa los PR en llamada, los otros tres aprueban y el CI está en verde antes de unir.
- **Cada archivo tiene dueño** (`.github/CODEOWNERS`). Solo se edita lo propio.
- **Commits**: `área: qué hiciste`, en presente (`motor:`, `ia:`, `ui:`, `data:`, `scripts:`, `tests:`, `docs:`, `chore:`, `fix:`).
- Las firmas de las funciones públicas están congeladas. Los archivos con `raise NotImplementedError` son esqueleto: se llenan sin cambiar la firma.

## Equipo

| Persona | Rol | Cuida |
| --- | --- | --- |
| Aleja (`alejac-beep`) | A | Datos y motor |
| Gaby (`gabriela708`) | B | Pantalla |
| Julian (`jdrodriguez03`) | C | IA y repositorio |
| Juanes (`juanesaacosta26`) | D | Pesos, soporte y pruebas |

## Más información

- `docs/00_LEER_PRIMERO_guia_rapida_del_repositorio.docx`: la guía de uso del repositorio (obligatoria).
- `docs/proyecto.docx`: la descripción completa del proyecto.
- `docs/plan_15_dias.docx` y `docs/guia_dia_por_dia.docx`: el plan y qué hace cada persona cada día.
- `docs/decisiones.md`: decisiones tomadas y pendientes.
- `CLAUDE.md`: reglas para los asistentes de código.
