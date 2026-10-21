# Radar de Decisiones

Herramienta para que un directivo de recursos humanos pruebe una decisión de compensación y vea, en segundos, qué muestran las empresas que ya la tomaron. No predice: compara contra 40 empresas reales y anonimizadas de una encuesta bimestral, calcula el costo en pesos y explica el resultado en tres oraciones escritas por IA, con cada cifra revisada antes de mostrarse.

Proyecto desarrollado para el concurso de Catch Consulting (México) con estudiantes de la Universidad Externado de Colombia, octubre de 2026.

**Pruébala en línea:** [radar-decisiones.streamlit.app](https://radar-decisiones.streamlit.app). La versión publicada funciona sin llave de API: los escenarios de referencia muestran explicaciones escritas por la IA y revisadas, y cualquier otra combinación usa la explicación de plantilla, con las mismas cifras. Si la app estuvo un tiempo sin visitas, puede tardar unos segundos en despertar.

## Características

- **Cinco palancas de compensación** (salario diario inicial, aguinaldo, prima vacacional, vales de despensa y rutas de transporte) que recalculan todo al instante.
- **Comparación contra empresas reales**: las que ya ofrecen ese nivel frente al resto, en rotación anual, bajas en los primeros tres meses y ausentismo.
- **Costos en pesos** de la medida y de la rotación actual, con supuestos que el directivo puede ajustar.
- **Explicación con IA** que nunca muestra una cifra que no esté en el cálculo, con respaldo automático si el modelo tarda o no hay internet.
- **Semáforo de evidencia** que indica qué tan sólida es la diferencia observada.
- **Escenarios guardados** que se comparan lado a lado y se descargan como informe PDF para el comité.
- **Modo sin conexión** para presentar sin depender de internet ni de la API.

## Contexto

Catch Consulting, firma de consultoría de México, organizó un concurso privado para estudiantes de la Universidad Externado de Colombia. Entregó a los equipos una base bimestral de recursos humanos y operaciones industriales de empresas reales y planteó un reto concreto: construir una herramienta que cualquier directivo pudiera usar sin instrucciones y que respondiera en vivo, durante la presentación, a los cambios que él mismo propusiera. El equipo tuvo quince días para diseñarla, construirla y probarla, y la presentó en una demostración en vivo de diez minutos. Catch autorizó publicar el proyecto completo, con sus datos.

## Requisitos

- Python 3.12
- Una llave de API de Anthropic, opcional. Sin ella la aplicación funciona igual y solo pierde la redacción en vivo de escenarios nuevos (ver [Configuración](#configuración)).

## Instalación

En Windows basta con hacer doble clic en `install.bat`, que crea el entorno `.venv` e instala las dependencias. En Mac o Linux:

```bash
git clone https://github.com/jdrodriguez03/radar-decisiones.git
cd radar-decisiones
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuración

La explicación en vivo usa un modelo de Claude y necesita una llave propia. Se crea en [console.anthropic.com](https://console.anthropic.com), en *API Keys*, y conviene fijar un límite de gasto mensual en *Limits*. Luego se copia el archivo de ejemplo y se reemplaza `sk-ant-xxxxxxxx` por la llave:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

`secrets.toml` está excluido de git y nunca debe subirse. La llave también puede ir en la variable de entorno `ANTHROPIC_API_KEY`, que es lo indicado si la aplicación se publica en un servidor o en Streamlit Community Cloud.

Los demás ajustes viven en `config.py`, entre ellos el modelo (`MODELO_IA`) y los tiempos límite de la IA. Los supuestos de costo por defecto, $15,000 por baja y $35,000 mensuales por ruta, están en `data/processed/supuestos.json` y también se pueden cambiar desde la aplicación.

## Uso

Con el entorno activo (en Windows, `.venv\Scripts\activate`):

```bash
streamlit run app.py
```

La aplicación se abre en `http://localhost:8501`. Una sesión típica sigue este orden:

1. **Elegir la empresa.** En la columna izquierda se escoge una de las 40 de la encuesta, o se captura una propia en «Mi empresa» con su plantilla, su rotación mensual y sus cinco prestaciones. Las marcadas con estrella son las que mejor ilustran la herramienta.
2. **Mover una prestación** con los botones − y + o el control deslizante. Las cifras del centro cambian al instante.
3. **Leer el comparativo.** La tabla del centro muestra tres columnas: «Situación actual», «Empresas con las medidas» y «Empresas sin las medidas». Debajo aparecen el costo anual de la medida (o el ahorro, si se bajó una prestación) y el costo anual de la brecha de rotación. En «Modificación de supuestos», el botón ⚙ cambia el costo por baja y el costo por ruta.
4. **Pulsar «Explicar»** para obtener las tres oraciones. Debajo, una gráfica ubica la rotación de la empresa frente a las empresas con y sin la medida, y el semáforo de evidencia dice si las que aplican la medida rotan menos o más y qué tan sólida es esa diferencia.
5. **Guardar escenarios** para compararlos y, con el botón que aparece bajo «Guardar escenario», **descargar el resumen en PDF** con la situación de la empresa, la tabla de escenarios y el detalle de cada uno.

«↻ Restablecer» devuelve las palancas al valor real de la empresa.

Para presentar sin internet se abre `scripts\demo_sin_internet.bat` (o `bash scripts/demo_sin_internet.sh`). En ese modo la aplicación no llama a la API y usa las explicaciones precalculadas o la plantilla. Antes de una sesión importante, `python scripts/verificar_demo.py` comprueba en menos de un minuto que todo esté en orden.

## Cómo funciona

Al mover una palanca, el motor separa a las demás empresas en dos conjuntos: las que ya ofrecen ese nivel o más (con la medida) y las demás (sin la medida). Si el primero tiene menos de cinco empresas se completa con las cinco más parecidas y la pantalla lo indica. Se comparan medianas y la solidez de la diferencia en rotación sale de una prueba de Mann-Whitney: clara con p < 0.05, débil con p < 0.15 y no concluyente en otro caso.

El resultado del motor es un JSON con estructura fija, validado contra `contrato/modelo.py`. La IA recibe solo ese JSON, y su texto pasa por un validador que descarta cualquier número que no aparezca ahí. Si el modelo no empieza a responder en 4 segundos, no termina en 8 o el texto no pasa la revisión, se muestra una explicación de plantilla con las mismas cifras.

## Estructura del proyecto

```
radar-decisiones/
├── app.py           # pantalla principal, une todas las piezas
├── config.py        # rutas, rangos de las palancas, umbrales y modelo de IA
├── motor/           # datos, grupo y resto, prueba estadística y costos
├── ia/              # prompts, llamada al modelo, plantilla, validador, caché y PDF
├── ui/              # una pieza de pantalla por archivo
├── contrato/        # estructura del JSON, ejemplo y casos de prueba
├── data/
│   ├── raw/         # bases de la encuesta en Excel
│   └── processed/   # parquet, supuestos y explicaciones precalculadas
├── scripts/         # preparación de datos, caché y verificaciones
├── sandbox/         # mini aplicaciones para probar cada pieza
├── tests/           # pruebas automáticas
└── docs/            # documentación del proyecto y de los datos
```

## Datos

La base proviene de una encuesta bimestral de recursos humanos y operaciones, con siete bimestres entre julio de 2024 y agosto de 2025. Las empresas aparecen como «COMPAÑIA N». Los datos se procesan siempre con scripts y nunca a mano:

```
BASE_HISTORICA.xlsx → scripts/historica_a_reducida.py → BASE_REDUCIDA_v2.xlsx
                    → scripts/preparar_datos.py       → empresas.parquet
```

`python scripts/historica_a_reducida.py --comparar data/raw/BASE_REDUCIDA_v2.xlsx` comprueba que la base reducida se reproduce exactamente desde la histórica. El significado de cada columna está en `docs/diccionario_reduccion.md`.

## Pruebas

```bash
pytest
ruff check .
```

Ninguna prueba llama a la API. Las dos corren en GitHub Actions con cada pull request y con cada cambio en `main`.

## Historial de desarrollo

El proyecto se construyó en quince días con ramas por integrante, pull requests revisados por el equipo y pruebas automáticas en cada cambio. Este repositorio es la copia pública del repositorio de trabajo: conserva todos los commits con sus fechas y autores, y los 32 pull requests están reunidos en [`docs/pull_requests.md`](docs/pull_requests.md), porque GitHub no los copia junto con el historial.

## Equipo

| Integrante | Rol |
| --- | --- |
| Alejandra Cortés ([@AlejaCortes](https://github.com/AlejaCortes)) | Datos y motor de comparación |
| Gabriela Chisaba ([@gabriela708](https://github.com/gabriela708)) | Diseño y pantalla |
| Julián David Rodríguez ([@jdrodriguez03](https://github.com/jdrodriguez03)) | Inteligencia artificial y repositorio |
| Juan Esteban Acosta ([@juanesaacosta26](https://github.com/juanesaacosta26)) | Costos, soporte de usuario y pruebas |

## Licencia

El código está bajo licencia [MIT](LICENSE). Los datos de `data/` pertenecen a la empresa dueña de la encuesta y se publican con su autorización solo para consultar y reproducir este proyecto.
