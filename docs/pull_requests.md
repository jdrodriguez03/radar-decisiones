# Pull requests del desarrollo

Este repositorio es la versión pública del proyecto. El trabajo se hizo en un repositorio privado del equipo, donde cada cambio entró por una rama propia y un pull request revisado por los demás antes de unirse a `main`. Al publicarlo se copió el historial completo, con sus fechas, autores y mensajes, pero se reemplazaron los correos personales por los correos privados de GitHub de cada integrante y se dejaron fuera los documentos internos de la presentación (guion, plan de trabajo y notas de coordinación).

Los pull requests son páginas de GitHub y no forman parte del historial de git, por eso no se copian con él y la pestaña «Pull requests» de este repositorio aparece vacía. Para no perder ese registro, este documento reúne los 32 en orden, con su autor, su fecha, lo que su autor escribió y los archivos que tocó. El commit de unión de cada uno, que en el historial empieza por «PR N», lleva también su título y su descripción.

| PR | Rama | Autor | Unido | Título |
| --- | --- | --- | --- | --- |
| 1 | `c/e1-reorganizar-carpetas` | Julián David Rodríguez | 05/10/2026 | chore: reorganizar carpetas (fixtures en contrato, sin pruebas/ ni Makefile) |
| 2 | `c/e1-ia` | Julián David Rodríguez | 07/10/2026 | ia: plantilla de respaldo y sandbox con streaming (bloque 1) |
| 3 | `b/e1-tema` | Gabriela Chisaba | cerrado sin unir | Tema oscuro y maqueta estatica de tres columnas |
| 4 | `d/e1-contrato` | Juan Esteban Acosta | 07/10/2026 | D · bloque 1: contrato validado, fixtures, pesos y supuestos |
| 5 | `a/e1-datos` | Alejandra Cortés | 07/10/2026 | A/e1 datos |
| 6 | `d/e2-selector` | Juan Esteban Acosta | 09/10/2026 | Bloque 2-D: Selector de empresa, panel ⚙ y etiquetas |
| 7 | `c/e2-explicar` | Julián David Rodríguez | 09/10/2026 | ia: explicar con límite, solo el último clic y respaldo sin internet (bloque 2) |
| 8 | `a/e2-motor` | Alejandra Cortés | 09/10/2026 | A/e2 motor |
| 9 | `b/e1-tema_correciones` | Gabriela Chisaba | 09/10/2026 | Correciones de tema |
| 10 | `b/e2-indicadores_simulados` | Gabriela Chisaba | 09/10/2026 | Indicadores simulados y comparativos |
| 11 | `c/e3-validador` | Julián David Rodríguez | 12/10/2026 | ia: validador de cifras, caché, métricas de negocio y panel de explicación (bloque 3) |
| 12 | `d/e3-combinaciones-guion` | Juan Esteban Acosta | 12/10/2026 | scripts: 20 combinaciones y guion_v1 |
| 13 | `b/e3-grafica_velocidad` | Gabriela Chisaba | 18/10/2026 | B/e3 grafica velocidad |
| 14 | `a/e3-motor` | Alejandra Cortés | 12/10/2026 | Anexo del motor sobre rasgos en común y el estado inicial |
| 15 | `d/e4-fixtures-reales` | Juan Esteban Acosta | 14/10/2026 | D/e4 fixtures reales |
| 16 | `c/e4-prompt-real` | Julián David Rodríguez | 14/10/2026 | ia: bloque 4 · prompt probado con 15 estados reales y botón Explicar |
| 17 | `d/e4-anomalias-completas` | Juan Esteban Acosta | 14/10/2026 | fix: restaurar regenerar_fixtures.py y completar anomalias y test_fixtures_reales |
| 18 | `a/e3-motor` | Alejandra Cortés | 17/10/2026 | motor: optimizar comparación y correcciones completado |
| 19 | `c/e6-cache` | Julián David Rodríguez | 17/10/2026 | c/e6-cache: caché completo y revisado, presentación de 10 minutos y semáforo de evidencia |
| 20 | `c/e6-criticas` | Julián David Rodríguez | 17/10/2026 | c/e6-criticas: las 4 críticas más probables del jurado, con respuesta y dueño |
| 21 | `a/e5-motor` | Alejandra Cortés | 18/10/2026 | motor: comparación de escenarios A y B |
| 22 | `c/e7-fix-semaforo` | Julián David Rodríguez | 18/10/2026 | c/e7-fix-semaforo: arregla el CI de main (semáforo con el motor nuevo) y trae las críticas del jurado |
| 23 | `c/e7-modo-demo` | Julián David Rodríguez | 18/10/2026 | ia: agrega MODO_DEMO para presentar sin internet |
| 24 | `d/e5-historial` | Juan Esteban Acosta | 18/10/2026 | D/e5 historial |
| 25 | `d/e6-guion` | Juan Esteban Acosta | 19/10/2026 | D/e6 guion |
| 26 | `a/e6-demo` | Alejandra Cortés | 19/10/2026 | Funcion install para la aplicacion |
| 27 | `d/e6-usabilidad` | Juan Esteban Acosta | 19/10/2026 | docs: resultados de la prueba con usuarios |
| 28 | `c/e7-resumen` | Julián David Rodríguez | 19/10/2026 | ia: informe en PDF para el comité (crítica 4) y texto cuando no hay con quién comparar |
| 29 | `d/e6-guion-v5` | Juan Esteban Acosta | 19/10/2026 | docs: guion v5 con el orden elegido por el equipo |
| 30 | `a/e7-usabilidad` | Alejandra Cortés | 20/10/2026 | Completa verificador y plan de contingencia de la demo |
| 31 | `b/integracion_total` | Gabriela Chisaba | 20/10/2026 | B/integracion total |
| 32 | `c/e8-v1` | Julián David Rodríguez | 20/10/2026 | docs: README de entrega, licencia del equipo y vocabulario nuevo en el PDF y la plantilla |

## PR 1 · chore: reorganizar carpetas (fixtures en contrato, sin pruebas/ ni Makefile)

Rama `c/e1-reorganizar-carpetas` · Julián David Rodríguez (@jdrodriguez03) · abierto el 05/10/2026, unido a `main` el 05/10/2026.

### Qué cambia
(1 o 2 líneas)

### Cómo probarlo
(comando o sandbox, y qué debe verse)

### Checklist
- [ ] Mi "Listo cuando" se cumple
- [ ] Respeta las firmas y el contrato
- [ ] Tiene al menos una prueba y el CI está en verde
- [ ] Solo toqué archivos de mi carpeta

Commit de unión: `a88f320`. Archivos que cambiaron (9): `.github/CODEOWNERS`, `CONTRIBUTING.md`, `Makefile`, `README.md`, `config.py`, `contrato/fixtures/.gitkeep`, `scripts/combinaciones.yaml`, `scripts/correr_combinaciones.py`, `tests/fixtures/.gitkeep`.

## PR 2 · ia: plantilla de respaldo y sandbox con streaming (bloque 1)

Rama `c/e1-ia` · Julián David Rodríguez (@jdrodriguez03) · abierto el 07/10/2026, unido a `main` el 07/10/2026.

### Qué cambia
- `ia/prompts.py`: prompt de sistema y `armar_mensaje`.
- `ia/plantilla.py`: `plantilla(estado)` con formatos de cifra (`22%`, `$6.3 millones`).
- `sandbox/c_explicacion.py`: explicación con streaming palabra por palabra, modo simulado o API real, con tiempos de primera palabra y texto completo.
- `tests/test_plantilla.py`: 3 pruebas.
- `config.py`: agrega `MODELO_IA`.

### Cómo probarlo
- `ruff check . && pytest` (4 pruebas en verde).
- `streamlit run sandbox/c_explicacion.py`: en «Simulado» escribe palabra por palabra; en «API real» (con llave en `secrets.toml`) la primera palabra llegó en 1.21 s y el texto completo en 2.35 s.

Commit de unión: `e93d370`. Archivos que cambiaron (5): `config.py`, `ia/plantilla.py`, `ia/prompts.py`, `sandbox/c_explicacion.py`, `tests/test_plantilla.py`.

## PR 3 · Tema oscuro y maqueta estatica de tres columnas

Rama `b/e1-tema` · Gabriela Chisaba (@gabriela708) · abierto el 07/10/2026 y cerrado sin unir; su contenido entró después en otros pull requests.

### Qué cambia
Establecer el tema oscuro, tamaño de letras y maqueta de tres columnas con palancas desactivadas
### Cómo probarlo:
La pantalla se parece a la maqueta del documento del proyecto con las cifras reales.


## PR 4 · D · bloque 1: contrato validado, fixtures, pesos y supuestos

Rama `d/e1-contrato` · Juan Esteban Acosta (@juanesaacosta26) · abierto el 07/10/2026, unido a `main` el 07/10/2026.

Sin descripción escrita.

Commit de unión: `892fb4e`. Archivos que cambiaron (11): `contrato/fixtures/01_aguinaldo.json`, `contrato/fixtures/02_prima.json`, `contrato/fixtures/03_salario.json`, `contrato/fixtures/04_ya_rota_menos.json`, `contrato/fixtures/05_inicial.json`, `contrato/modelo.py`, `data/processed/supuestos.json`, `motor/pesos.py`, `tests/test_contrato.py`, `tests/test_fixtures.py`, `tests/test_pesos.py`.

## PR 5 · A/e1 datos

Rama `a/e1-datos` · Alejandra Cortés (@AlejaCortes) · abierto el 07/10/2026, unido a `main` el 07/10/2026.

#Preparación y calidad de los datos
### Qué cambia
Se implementó la preparación y validación de los datos de empresas. Se generó el archivo empresas.parquet y se incorporó la carga y las pruebas de calidad de los datos correspondientes a los días 1 y 2.

### Cómo probarlo
ruff check .
pytest

También se puede verificar que empresas.parquet contenga las 40 empresas y que las pruebas de carga y calidad de datos se ejecuten correctamente.

Commit de unión: `ffdaf3c`. Archivos que cambiaron (7): `data/processed/empresas.parquet`, `motor/datos.py`, `scripts/generar_calidad_datos.py`, `scripts/preparar_datos.py`, `tests/test_calidad_datos.py`, `tests/test_datos.py`, `tests/test_preparar.py`.

## PR 6 · Bloque 2-D: Selector de empresa, panel ⚙ y etiquetas

Rama `d/e2-selector` · Juan Esteban Acosta (@juanesaacosta26) · abierto el 09/10/2026, unido a `main` el 09/10/2026.

### Qué cambia
Selector de empresa (ui/selector.py), panel ⚙ de supuestos (ui/supuestos.py) y etiquetas observado/calculado/supuesto (ui/procedencia.py), con sus sandbox y pruebas.

### Cómo probarlo
pytest tests/test_selector.py tests/test_soporte.py streamlit run sandbox/d_selector.py → COMPAÑIA 36 con todos los ✅ streamlit run sandbox/d_soporte.py → en ⚙, costo por baja 30000: la brecha pasa de $6.3 M a $12.7 M.

Commit de unión: `133f70a`. Archivos que cambiaron (7): `sandbox/d_selector.py`, `sandbox/d_soporte.py`, `tests/test_selector.py`, `tests/test_soporte.py`, `ui/procedencia.py`, `ui/selector.py`, `ui/supuestos.py`.

## PR 7 · ia: explicar con límite, solo el último clic y respaldo sin internet (bloque 2)

Rama `c/e2-explicar` · Julián David Rodríguez (@jdrodriguez03) · abierto el 09/10/2026, unido a `main` el 09/10/2026.

### Qué cambia
IA del bloque 2 (días 3 y 4) en ia/: explicar() con streaming, límite de 4 s y respaldo con plantilla; solo explica el último clic (corta la explicación vieja y cierra la conexión); el mensaje dice qué cambió frente al paso anterior; plantilla para el estado inicial. Además: modelo cambiado a claude-sonnet-5-5 (Haiku 4.5 tiene retiro agendado no antes del 15 de octubre) y propuesta de botón "Explicar" para discutir en el cierre (docs/propuesta_boton_explicar.md).

### Cómo probarlo
- `pytest -q` → 57 passed; `ruff check .` → limpio.
- `streamlit run sandbox/c_explicacion.py`:
  - "API real", pasos 01 a 05: textos como los de docs/pruebas_ia.md, primera palabra < 1 s.
  - "API lenta": a los 4 s sale la plantilla; si se cambia el radio antes, la página responde al instante (clic nuevo).
  - Sin wifi: la plantilla sale en < 0.1 s y sin errores, también en el 05 (estado inicial).

Commit de unión: `6d4cc78`. Archivos que cambiaron (9): `config.py`, `docs/pruebas_ia.md`, `ia/explicar.py`, `ia/plantilla.py`, `ia/prompts.py`, `sandbox/c_explicacion.py`, `tests/test_explicar.py`, `tests/test_plantilla.py`, `tests/test_prompts.py`.

## PR 8 · A/e2 motor

Rama `a/e2-motor` · Alejandra Cortés (@AlejaCortes) · abierto el 09/10/2026, unido a `main` el 09/10/2026.

### Qué cambia
Se implementó el filtro de empresas según las palancas movidas y la comparación entre el grupo y el resto. También se agregó la función para completar grupos pequeños con empresas similares por medio de la función KNN y calcular la señal estadística con Mann-Whitney para ver si las diferencias entre grupos son significativas en realidad o fue producto del azar.

### Cómo probarlo
Ejecutar pytest tests/test_comparar.py tests/test_completar_senal.py para verificar las pruebas del filtro, la búsqueda de empresas similares y el cálculo de la señal estadística, en diferentes escenarios posibles.

También ejecutar ruff check . y pytest para comprobar el código y las pruebas del proyecto.

Commit de unión: `d75ee9a`. Archivos que cambiaron (3): `motor/comparar.py`, `tests/test_comparar.py`, `tests/test_completar_senal.py`.

## PR 9 · Correciones de tema

Rama `b/e1-tema_correciones` · Gabriela Chisaba (@gabriela708) · abierto el 09/10/2026, unido a `main` el 09/10/2026.

### Qué cambia
Correcciones del primer bloque (temas y plantilla)

Commit de unión: `0cd5416`. Archivos que cambiaron (5): `.streamlit/config.toml`, `app.py`, `sandbox/b_controles.py`, `ui/controles.py`, `ui/tema.py`.

## PR 10 · Indicadores simulados y comparativos

Rama `b/e2-indicadores_simulados` · Gabriela Chisaba (@gabriela708) · abierto el 09/10/2026, unido a `main` el 09/10/2026.

### Qué cambia
Creación de la pantalla de comparaciones

Commit de unión: `4779d00`. Archivos que cambiaron (4): `sandbox/b_pantalla.py`, `ui/comparativo.py`, `ui/controles.py`, `ui/tema.py`.

## PR 11 · ia: validador de cifras, caché, métricas de negocio y panel de explicación (bloque 3)

Rama `c/e3-validador` · Julián David Rodríguez (@jdrodriguez03) · abierto el 10/10/2026, unido a `main` el 12/10/2026.

### Qué cambia
- **Validador de cifras** (`ia/validador.py`): ningún número llega a la pantalla si no está en los datos, en el paso anterior, en las métricas precalculadas o en los números del idioma (100, 3 y 12). Acepta redondeo hacia abajo (0.516 se puede escribir como 51% o 52%).
- **Validar antes de mostrar** (`ia/explicar.py`): la IA escribe en silencio, se valida el texto completo y solo después aparece con efecto de escritura (30 ms por palabra). Mientras tanto se ve "Analizando las empresas…". Límites: 4 s para empezar y 8 s para terminar; si no, plantilla.
- **Caché de explicaciones** (`ia/cache.py`, `ia/precalcular.py`, `scripts/generar_cache.py`): los 7 estados del guion responden al instante y sin internet. La llave incluye empresa, palancas movidas, costo por baja y paso anterior. Todo texto del caché vuelve a pasar el validador.
- **Métricas de negocio precalculadas** (`ia/derivadas.py`): personas que pierde al año, bajas antes de 3 meses, qué tan común es la medida, % de la nómina base y personas de diferencia. Las calcula el código; la IA solo las redacta.
- **Prompt**: máximo 75 palabras, sin cuentas propias, proporciones con palabras ("la mitad") y sin explicar por qué la señal es como es.
- **Plantilla reescrita**: mismas reglas que el prompt, nombra todas las palancas movidas y avisa cuando la señal es débil, no concluyente o el grupo se completó.
- **Panel derecho** (`ui/explicacion.render`): texto, señal y n.
- **Sandbox nuevo** (`sandbox/c_panel.py`): el panel como lo ve el público, con 6 escenarios (caché, IA en vivo, sin internet, IA que inventa, IA lenta) y "detrás de escena".
- **Plan actualizado con el botón Explicar** (decidido en el cierre del bloque 2): guía día por día, plan de 15 días, propuesta y registro de decisiones. Quedan tareas en los días 7, 8, 10, 11 y 16.

### Cómo probarlo
- `ruff check . && pytest -q` → 143 passed.
- `streamlit run sandbox/c_panel.py`:
  - "Como en la demo", pasos 1 a 3 → responde el caché.
  - "IA que inventa una cifra" → la cifra 31 nunca aparece; sale la plantilla.
  - "Sin internet, con caché" → el guion sigue funcionando.
- `streamlit run sandbox/c_explicacion.py` → laboratorio del prompt con la revisión de cifras.
- `docs/guia_dia_por_dia.docx`, días 7 y 8 → las tareas del botón Explicar para Gaby y Julian.

### Para avisar al equipo
- **Todos:** la explicación tarda unos 2–3 s en aparecer, a cambio de que nunca se muestre una cifra sin validar. Con el botón, esa espera solo ocurre cuando el usuario pulsa Explicar.
- **Gaby:** el día 7 conectas el botón Explicar y el panel con `ui.explicacion.render(contenedor, estado, anterior)`. El `anterior` es la última combinación explicada. Los parámetros `cliente` y `cache` son opcionales y solo los usa el sandbox.
- **Juanes:** las métricas nuevas (742 personas, 58% del mercado, 1.4% contra 10.3% de la nómina) cambian lo que puede decir el presentador. El guion v2 (día 11) debe decir quién pulsa Explicar en cada paso.
- **Aleja:** pendiente para el contrato la métrica de posición ("pierde más que 27 de 39"), y que `en_comun` no mande rasgos de palancas ya movidas.
- **Firmas:** `es_valido`, `explicar` y `render` ganaron parámetros **opcionales**; nada de lo existente cambia. `armar_mensaje` usa la nueva `anterior_util`, con la misma regla de antes.
- **Por decidir:** un caché que guarde lo que la IA responde en vivo, como extra del bloque 5.

Commit de unión: `df51ae9`. Archivos que cambiaron (20): `config.py`, `data/processed/cache.json`, `ia/cache.py`, `ia/derivadas.py`, `ia/explicar.py`, `ia/plantilla.py`, `ia/precalcular.py`, `ia/prompts.py`, `ia/validador.py`, `sandbox/c_explicacion.py`, `sandbox/c_panel.py`, `scripts/generar_cache.py`, `tests/test_cache.py`, `tests/test_derivadas.py`, `tests/test_explicacion.py`, `tests/test_explicar.py`, `tests/test_plantilla.py`, `tests/test_prompts.py`, `tests/test_validador.py`, `ui/explicacion.py`.

## PR 12 · scripts: 20 combinaciones y guion_v1

Rama `d/e3-combinaciones-guion` · Juan Esteban Acosta (@juanesaacosta26) · abierto el 10/10/2026, unido a `main` el 12/10/2026.

### Qué cambia
Las 20 combinaciones de prueba (`scripts/combinaciones.yaml` y `scripts/correr_combinaciones.py`), que generan `docs/resultados_combinaciones.md` con alertas, y el guion v1 en `docs/guion.md`. Incluye 5 pruebas nuevas en `tests/test_combinaciones.py`.

### Cómo probarlo
`python scripts/correr_combinaciones.py` debe imprimir "Listo: 20 casos" y "Con alerta: 4". En `docs/resultados_combinaciones.md`, G1, G2 y G3 dicen "coincide" (22 empresas, 22% contra 53%; 16 empresas, 17% contra 43%; 5 empresas, 12% contra 38%). `pytest tests/test_combinaciones.py` en verde. `docs/guion.md` se lee en menos de 5 minutos.

Commit de unión: `32b5bdb`. Archivos que cambiaron (4): `docs/resultados_combinaciones.md`, `scripts/combinaciones.yaml`, `scripts/correr_combinaciones.py`, `tests/test_combinaciones.py`.

## PR 13 · B/e3 grafica velocidad

Rama `b/e3-grafica_velocidad` · Gabriela Chisaba (@gabriela708) · abierto el 11/10/2026, unido a `main` el 18/10/2026.

### Qué cambia
Grafica de cambio en la rotación anual según la palanca modificada y medición de tiempo del dibujo.
Reorganización del front.
Verificación de botones.
Conectar todo.
Botón explicar.

### Cómo probarlo
Con streamlit run app.py

Commit de unión: `2bb15ba`. Archivos que cambiaron (12): `.streamlit/config.toml`, `app.py`, `sandbox/b_botones.py`, `sandbox/b_pantalla.py`, `sandbox/b_restablecer.py`, `tests/test_controles.py`, `tests/test_extras.py`, `tests/test_selector.py`, `ui/comparativo.py`, `ui/controles.py`, `ui/selector.py`, `ui/tema.py`.

## PR 14 · Anexo del motor sobre rasgos en común y el estado inicial

Rama `a/e3-motor` · Alejandra Cortés (@AlejaCortes) · abierto el 12/10/2026, unido a `main` el 12/10/2026.

### Qué cambia
Se crea función que revisa características y diferencias principales entre grupos con o sin las palancas, además se verifica el estado en el que se encuentra que sintetiza toda la info, se crean los respectivos test y un sandbox de prueba.
### Cómo probarlo
El comando o el sandbox, y qué se debe ver. Ejemplo: "pytest tests/test_motor.py; en el sandbox, aguinaldo a 20 muestra n = 22".

Commit de unión: `cf18ef3`. Archivos que cambiaron (6): `motor/api.py`, `motor/en_comun.py`, `sandbox/a_motor.py`, `tests/test_api.py`, `tests/test_comparar.py`, `tests/test_en_comun.py`.

## PR 15 · D/e4 fixtures reales

Rama `d/e4-fixtures-reales` · Juan Esteban Acosta (@juanesaacosta26) · abierto el 14/10/2026, unido a `main` el 14/10/2026.

### Qué cambia
Las 20 combinaciones y los 5 fixtures ahora salen del motor real (`motor.api.calcular_estado`), y las anomalías quedan explicadas en `docs/anomalias.md` (día 7). Además, `tests/test_guion.py` protege las cifras del guion, y el guion v1.1 suma las empresas de respaldo COMPAÑIA 29 y 15 (día 8).

**Archivos:**
- `scripts/correr_combinaciones.py`: usa `calcular_estado` en vez de `comparar` + `pesos`; agrega `perfil_de_empresa`, `cambio_de` y `estado_de_caso` (Julian puede reutilizar esta última para sus 15 estados).
- `scripts/regenerar_fixtures.py` (nuevo): regenera los 5 fixtures sin cambiar sus nombres, los valida contra `contrato/modelo.py` y revisa que cada uno siga cumpliendo su papel.
- `contrato/fixtures/*.json`: salida real del motor. Del 01 al 04 no cambian las cifras; el 05 ahora trae los ids de las 39 empresas.
- `docs/resultados_combinaciones.md` y `docs/anomalias.md`: 4 casos con alerta y 3 vigilados, cada uno con cómo explicarlo en la demo.
- `tests/test_combinaciones.py` (5 pruebas nuevas), `tests/test_fixtures_reales.py` (nuevo) y `tests/test_guion.py` (nuevo).
- `docs/guion.md` v1.1: sección 4 (empresas de respaldo) y sección 5 (riesgo de valores fuera del rango de los controles).

### Cómo probarlo
    python scripts/regenerar_fixtures.py --revisar   # no debe mostrar cambios en las cifras de 01 a 04
    python scripts/correr_combinaciones.py           # "Listo: 20 casos", 4 con alerta, sin "¡Ojo!"
    pytest tests/test_guion.py -v

Se debe ver:
- Paso 1: 22 empresas, 22% contra 53%, señal clara, $2.3 M y $6.3 M.
- Paso 2: 16 empresas, 17% contra 43%, débil, $3.7 M y $7.4 M.
- Paso 3: 5 empresas, 12% contra 38%, no concluyente, sin completado.
- Con $30,000 por baja, la brecha pasa de $8.5 M a $17.1 M.

### Para decidir en esta revisión
1. **Completado (Aleja):** hoy el grupo completado *reemplaza* a las empresas que sí cumplen. En E1, COMPAÑIA 19 paga $449 y queda fuera del grupo de "$380 o más". ¿Conservamos a las que cumplen y solo agregamos similares? (ver `docs/anomalias.md`, Problema 1)
2. **COMPAÑIA 27 (Aleja):** tiene plantilla 0 y entra en todos los grupos de salario. ¿La excluimos?
3. **Vales de COMPAÑIA 15 (Gaby):** su valor real (4.5%) está por debajo del mínimo del control (6%). Al abrirla en la app, `palancas_movidas` debe salir vacío.
4. **Caché (Julian):** agregar el paso 1 de COMPAÑIA 15 (salario a $340), que no está en `combinaciones.yaml`.

Si se cambia el completado, corro de nuevo los dos scripts y `test_fixtures_reales.py` y `test_guion.py` avisarán qué cifras se movieron.

Commit de unión: `c5fdfaf`. Archivos que cambiaron (6): `docs/anomalias.md`, `docs/resultados_combinaciones.md`, `scripts/correr_combinaciones.py`, `scripts/regenerar_fixtures.py`, `tests/test_combinaciones.py`, `tests/test_fixtures_reales.py`.

## PR 16 · ia: bloque 4 · prompt probado con 15 estados reales y botón Explicar

Rama `c/e4-prompt-real` · Julián David Rodríguez (@jdrodriguez03) · abierto el 14/10/2026, unido a `main` el 14/10/2026.

### Qué cambia

Bloque 4 de Julian (días 7 y 8): la IA probada con 15 estados reales del motor (**15 de 15 cumplen todas las reglas**), las reglas de lenguaje revisadas en código y el botón **Explicar** del lado de la IA.

- **`ia/reglas.py` (nuevo):** revisa la forma del texto. Lo grave (palabras de causa y advertencia faltante) se revisa **en vivo**: si falla, sale la plantilla, igual que con una cifra inventada. El resto (largo, jerga, "N empresas") se revisa en pruebas.
- **Botón Explicar:** `armar_mensaje` nombra **todas** las palancas que cambiaron desde la última explicación (nuevas, cambiadas, quitadas y las que ya tenía). `ui/explicacion.py` suma `falta_explicar`, `aviso_pendiente` y `mostrar`. El código para `app.py` está en `docs/propuesta_boton_explicar.md` (Gaby).
- **Prompt afinado con datos reales:** aviso escrito cuando la señal es no concluyente o el grupo se completó, sin rasgo en ese caso; "ninguna" para 0 de N; sin "mediano" en los rasgos; montos de menos de un millón en miles; "las otras N empresas" si el resto es muy chico; `pulir()` arregla palabras pegadas.
- **Validador:** acepta montos en miles ("$250 mil") y los ahorros en positivo (costo negativo).
- **`scripts/probar_ia.py` + `docs/textos_ia.json` + `tests/test_reglas_ia.py`:** los 15 textos se guardan con su estado y se vuelven a revisar en cada PR **sin llamar a la IA**.
- **`sandbox/c_boton.py`:** el botón Explicar con el motor real y lo que se le manda a la IA.

Detalle completo y hallazgos en `docs/pruebas_ia.md`, sección "Días 7 y 8".

### Para el equipo (se comenta en la llamada)

- **La temperatura no se puede usar:** `anthropic==1.11.0` ya no acepta `temperature`; mandarla hacía caer **todas** las explicaciones a la plantilla. Se quitó, y una prueba evita que vuelva.
- **Tiempos agotados:** 2 en unas 30 llamadas, a los 8 s. En vivo sale la plantilla (lo diseñado); por eso el caché del guion del día 11 es clave.
- **Punto de control:** con el motor real, "salario a $350" da 5 empresas **sin** grupo completado, pero la lista espera el aviso de completado (Aleja y Juanes).
- **`app.py` en main** sigue siendo la maqueta del día 2: la integración (Gaby) aún no está fusionada.
- `ia/cache.py`: `_firma` pasó a `firma` (la usa `ui/explicacion.py`); solo cambia el nombre.

### Cómo probarlo

```bash
pytest -q                        # 244 passed (46 revisan los 15 textos reales)
streamlit run sandbox/c_boton.py
```

En el sandbox: aguinaldo a 20 y pulsar **Explicar** → texto de 22 empresas. Mover prima a 0.5 y salario a 350 sin pulsar → el texto viejo se oculta, sale el aviso y "Detrás de escena" muestra las **dos** palancas nuevas. Pulsar Explicar → texto de 5 empresas.

Commit de unión: `37d6258`. Archivos que cambiaron (16): `docs/pruebas_ia.md`, `docs/textos_ia.json`, `ia/cache.py`, `ia/explicar.py`, `ia/prompts.py`, `ia/reglas.py`, `ia/validador.py`, `sandbox/c_boton.py`, `scripts/probar_ia.py`, `tests/test_boton_explicar.py`, `tests/test_explicar.py`, `tests/test_prompts.py`, `tests/test_reglas.py`, `tests/test_reglas_ia.py`, `tests/test_validador.py`, `ui/explicacion.py`.

## PR 17 · fix: restaurar regenerar_fixtures.py y completar anomalias y test_fixtures_reales

Rama `d/e4-anomalias-completas` · Juan Esteban Acosta (@juanesaacosta26) · abierto el 14/10/2026, unido a `main` el 14/10/2026.

Sin descripción escrita.

Commit de unión: `5954e0a`. Archivos que cambiaron (3): `docs/anomalias.md`, `scripts/regenerar_fixtures.py`, `tests/test_fixtures_reales.py`.

## PR 18 · motor: optimizar comparación y correcciones completado

Rama `a/e3-motor` · Alejandra Cortés (@AlejaCortes) · abierto el 15/10/2026, unido a `main` el 17/10/2026.

### Qué cambia
Se optimiza la lógica del motor para comparar escenarios y completar señales, y se ajustan las pruebas correspondientes para verificar su funcionamiento.

### Cómo probarlo
Ejecutar python -m ruff check . y python -m pytest -v. Se espera que Ruff no reporte errores y que las pruebas finalicen correctamente.

Commit de unión: `53420a4`. Archivos que cambiaron (6): `motor/api.py`, `motor/comparar.py`, `motor/en_comun.py`, `tests/test_api.py`, `tests/test_completar_senal.py`, `tests/test_en_comun.py`.

## PR 19 · c/e6-cache: caché completo y revisado, presentación de 10 minutos y semáforo de evidencia

Rama `c/e6-cache` · Julián David Rodríguez (@jdrodriguez03) · abierto el 17/10/2026, unido a `main` el 17/10/2026.

### Qué cambia
Días 11 y 12 de Julian, más el extra del bloque 5. Son 4 commits:

1. **docs: la presentación dura 10 minutos desde que se conecta el PC.** Plan, guía día por día, `docs/guion.md` (solo la duración y los pendientes; la tabla minuto a minuto de Juanes no cambió) y `docs/decisiones.md`. Meta: terminar en 8 minutos.
2. **ia: caché completo.** 26 explicaciones en `data/processed/cache.json`: el guion de COMPAÑIA 36 (incluido el costo por baja a $30,000 en el minuto 3:45), los respaldos de COMPAÑIA 29 y COMPAÑIA 15, y las 20 combinaciones de `combinaciones.yaml`. Generadas con el motor real y el prompt actual. La IA ahora también recibe el cambio del costo por baja (`ia/prompts.py`).
3. **scripts: revisión del caché sin internet** (`scripts/revisar_cache.py`). 26 de 26 pasos sin problemas y todos salen del caché al instante. El paso de $30,000 se recortó a mano (estaba largo y tenía una cifra que se leía mal) y quedó marcado con `editado_a_mano`.
4. **ia: semáforo de evidencia** (`ia/semaforo.py` y `ui/explicacion.py`). **Decisión de Julian: reemplaza a la pregunta libre** como extra del bloque 5. Dos apartados: *Dirección* («↓ Rotan menos», o una alerta roja «⚠ Rotan más») y *Solidez* (barra verde, amarilla o naranja con la señal estadística del motor), más la frase de los pesos. Se calcula con el contrato, sin IA ni internet. No dice que la medida funcione: describe lo que muestran las empresas que ya lo hacen.

### Cómo probarlo
- `pytest` → **295 passed**, y `ruff check .` limpio.
- `python scripts/revisar_cache.py` → **26 de 26 pasos sin problemas**.
- `streamlit run sandbox/c_entrega.py` → toda la entrega en una pantalla: cada paso con su semáforo y su explicación (dice si sale del caché, de la IA o de la plantilla), y la pestaña de revisión del caché.
- `streamlit run sandbox/c_semaforo.py` → el semáforo de los 26 pasos.

### Para el equipo
- **Gaby:** el semáforo está listo para conectar con `EXTRAS["semaforo"]`. Las líneas para `app.py`, y cómo mover las tres piezas (dirección, solidez y pesos) por separado, están en `docs/semaforo_para_gaby.md`. Para el ensayo de mañana, tu integración tiene que estar en main.
- **Juanes:** confirma en el guion v2 (1) que se pulsa Explicar después de cambiar el costo a $30,000, y (2) que las historias de respaldo siguen siendo las de COMPAÑIA 29 y COMPAÑIA 15. El caché las tiene así.
- **Todos:**
  - No cambien los valores por defecto de `data/processed/supuestos.json`: el caché quedaría inválido.
  - No usen `python scripts/generar_cache.py --rehacer`: borra el texto corregido a mano.
- **Pendiente con la dirección:** ¿las preguntas del jurado entran en los 10 minutos?
- **Llaves de la API:** una por lugar, nunca compartida por chat. Detalle en `docs/decisiones.md`.

Commit de unión: `62f90d4`. Archivos que cambiaron (13): `data/processed/cache.json`, `docs/revision_cache.md`, `ia/prompts.py`, `ia/semaforo.py`, `sandbox/c_entrega.py`, `sandbox/c_semaforo.py`, `scripts/generar_cache.py`, `scripts/revisar_cache.py`, `tests/test_generar_cache.py`, `tests/test_prompts.py`, `tests/test_revisar_cache.py`, `tests/test_semaforo.py`, `ui/explicacion.py`.

## PR 20 · c/e6-criticas: las 4 críticas más probables del jurado, con respuesta y dueño

Rama `c/e6-criticas` · Julián David Rodríguez (@jdrodriguez03) · abierto el 17/10/2026, unido a `c/e6-cache` el 17/10/2026.

### Qué cambia
Las 4 críticas más probables del jurado (de una revisión de la app como directivo de consultora), con su respuesta de dos frases y su dueño. Nuevo `docs/criticas_jurado.md`; las tareas quedan en el plan (bloques 6 y 7, y una fila en riesgos), en la guía día por día (días 12 a 14) y en `docs/decisiones.md`.

Este PR sale de `c/e6-cache` (PR PR 19): se fusiona después de él.

### Cómo probarlo
Leer `docs/criticas_jurado.md` y revisar en el plan y la guía las tareas de cada uno. Solo cambian documentos.

### Para el equipo
- **Juanes (días 12 y 13):** las respuestas al guion, máximo 2 movimientos del juez y leer en voz alta «qué tienen en común».
- **Gaby (día 13, antes del ensayo 1):** el supuesto del costo por baja visible junto a la brecha.
- **Julian (día 14):** el botón «Descargar resumen», solo si los ensayos salen bien.

Solo cambió documentos internos de la presentación, que no forman parte de esta versión, por eso su commit de unión no aparece en el historial público.

## PR 21 · motor: comparación de escenarios A y B

Rama `a/e5-motor` · Alejandra Cortés (@AlejaCortes) · abierto el 17/10/2026, unido a `main` el 18/10/2026.

### Qué cambia
Se agregó la funcionalidad para guardar hasta dos escenarios y comparar sus resultados. Se creó una interfaz en sandbox/a_escenarios.py para visualizar los escenarios A y B y sus diferencias.

### Cómo probarlo
Ejecutar pytest para comprobar que las pruebas pasan. Abrir el sandbox de escenarios y guardar dos escenarios de la misma empresa con diferentes valores de las palancas. Se debe poder visualizar la comparación de sus resultados, incluyendo el tamaño del grupo y el costo de la medid

Commit de unión: `f23d9e1`. Archivos que cambiaron (3): `sandbox/a_escenarios.py`, `tests/test_escenarios.py`, `ui/escenarios.py`.

## PR 22 · c/e7-fix-semaforo: arregla el CI de main (semáforo con el motor nuevo) y trae las críticas del jurado

Rama `c/e7-fix-semaforo` · Julián David Rodríguez (@jdrodriguez03) · abierto el 18/10/2026, unido a `main` el 18/10/2026.

### Qué cambia
Arregla el CI rojo de main. El PR 18 (motor nuevo de Aleja: el completado conserva a las empresas que sí cumplen) y el PR 19 (semáforo) pasaron el CI por separado, pero al juntarse dos pruebas del semáforo quedaron esperando las cifras del motor anterior.

- **`tests/test_semaforo.py`:** E1 ya no espera alerta (con el motor nuevo rota menos: 10% contra 39%). La frase «cuesta más» se prueba con R15-2 en lugar de E4, porque E4 ahora tiene brecha $0. Prueba nueva para E1 que deja escrito el comportamiento actual. El código del semáforo no cambia.
- **`ia/precalcular.py`:** `generar_cache.py` vuelve a pedir los textos que ya no pasan el validador y conserva los que siguen siendo válidos (incluidos los editados a mano). Así, si el motor vuelve a cambiar, basta con correr el script. Dos pruebas nuevas en `tests/test_cache.py`.
- **`data/processed/cache.json`:** se regeneraron E1, E3 y E4; el texto de E4 se corrigió a mano (estaba largo y decía «así que»).
- **Documentos:** trae a main las críticas del jurado (`docs/criticas_jurado.md`, plan, guía y decisiones). El PR 20 se fusionó en `c/e6-cache` y no había llegado a main.

### Cómo probarlo
- `pytest` → **309 passed**, y `ruff check .` limpio.
- `python scripts/revisar_cache.py` → **26 de 26**.

### Para el equipo
- **Aleja (PR 21) y Gaby (PR 13):** cuando se fusione este PR, pulsen **"Update branch"** en el suyo para que el CI se vuelva a correr con el arreglo. Gaby: además, `ruff check --fix sandbox/b_restablecer.py`.
- **Juanes:** actualizar E1 y E4 en la sección 2 de `docs/guion.md` y en `docs/anomalias.md` (E1: 10% contra 39%; E4: 60% contra 29%, brecha $0). El guion principal no cambió.
- **Para que no se repita:** antes de fusionar un PR, si main cambió desde su último CI, pulsar "Update branch" y esperar el verde.

Commit de unión: `117f6c1`. Archivos que cambiaron (5): `data/processed/cache.json`, `docs/revision_cache.md`, `ia/precalcular.py`, `tests/test_cache.py`, `tests/test_semaforo.py`.

## PR 23 · ia: agrega MODO_DEMO para presentar sin internet

Rama `c/e7-modo-demo` · Julián David Rodríguez (@jdrodriguez03) · abierto el 18/10/2026, unido a `main` el 18/10/2026.

### Qué cambia
Con la variable `MODO_DEMO=1`, la app nunca llama a la API: cada explicación sale del caché y, si no está ahí, de la plantilla. Sirve si en la sala el wifi falla o la API va lenta: la explicación sale al instante en vez de esperar hasta 4 s.

- `ia/explicar.py`: función `modo_demo()`; si está activo, se salta la IA después de buscar en el caché.
- `scripts/demo_sin_internet.bat` (Windows) y `.sh` (Git Bash): abren la app con el modo encendido, con doble clic.
- `.gitattributes`: los `.bat` se guardan con saltos de línea de Windows (si no, el doble clic falla).
- `README.md`: cómo usar el lanzador.
- `tests/test_modo_demo.py`: 16 pruebas, incluida una que falla si con el modo encendido se llega a llamar a la API.

### Cómo probarlo
1. `pytest tests/test_modo_demo.py` → 16 passed (la suite completa: 325 passed).
2. Doble clic en `scripts/demo_sin_internet.bat`: la terminal dice "MODO_DEMO encendido" y abre la app.
3. Ya probado: un estado que no está en el caché tarda 2.14 s con la IA y 0.00 s con MODO_DEMO (sale de la plantilla).

Ojo: en `main`, `app.py` todavía es la maqueta y no llama a `explicar`, así que en la app el cambio se nota cuando se fusione el PR PR 13 de Gaby. Sin `MODO_DEMO`, la app funciona igual que antes.

Commit de unión: `9639f30`. Archivos que cambiaron (6): `.gitattributes`, `README.md`, `ia/explicar.py`, `scripts/demo_sin_internet.bat`, `scripts/demo_sin_internet.sh`, `tests/test_modo_demo.py`.

## PR 24 · D/e5 historial

Rama `d/e5-historial` · Juan Esteban Acosta (@juanesaacosta26) · abierto el 18/10/2026, unido a `main` el 18/10/2026.

Sin descripción escrita.

Commit de unión: `f0daee7`. Archivos que cambiaron (5): `docs/usabilidad.md`, `sandbox/d_historial.py`, `tests/test_historial.py`, `tests/test_usabilidad.py`, `ui/historial.py`.

## PR 25 · D/e6 guion

Rama `d/e6-guion` · Juan Esteban Acosta (@juanesaacosta26) · abierto el 19/10/2026, unido a `main` el 19/10/2026.

Sin descripción escrita.

Commit de unión: `2f69613`. Archivos que cambiaron (2): `docs/anomalias.md`, `docs/resultados_combinaciones.md`.

## PR 26 · Funcion install para la aplicacion

Rama `a/e6-demo` · Alejandra Cortés (@AlejaCortes) · abierto el 19/10/2026, unido a `main` el 19/10/2026.

### Qué cambia
Install crea el entorno e instala todo

### Cómo probarlo
El comando para correrlo es " .\.venv\Scripts\python.exe -m streamlit run app.py"

Sí puede ayudar a preparar la laptop para funcionar sin internet, pero hay que ejecutar el instalador antes de desconectarse: la primera instalación puede necesitar internet para descargar los paquetes. Una vez instalados, la app puede usar los datos y el caché locales. Para evitar que intente llamar a la API cuando falte una explicación en caché, inicia la app con el modo demo activado:
$env:MODO_DEMO = "1"
.\.venv\Scripts\python.exe -m streamlit run app.py
Con MODO_DEMO=1, la lógica actual usa el caché disponible o una plantilla de respaldo y no llama a la API. Por tanto, una explicación que no esté precalculada no será una respuesta nueva de IA: se mostrará mediante la plantilla. La app local y Streamlit Cloud son instalaciones separadas; para garantizar el modo demo en Cloud, hay que configurar MODO_DEMO = "1" en los Secrets de esa aplicación.

Commit de unión: `66c6c53`. Archivos que cambiaron (1): `install.bat`.

## PR 27 · docs: resultados de la prueba con usuarios

Rama `d/e6-usabilidad` · Juan Esteban Acosta (@juanesaacosta26) · abierto el 19/10/2026, unido a `main` el 19/10/2026.

Sin descripción escrita.

Commit de unión: `93b8236`. Archivos que cambiaron (1): `docs/usabilidad.md`.

## PR 28 · ia: informe en PDF para el comité (crítica 4) y texto cuando no hay con quién comparar

Rama `c/e7-resumen` · Julián David Rodríguez (@jdrodriguez03) · abierto el 19/10/2026, unido a `main` el 19/10/2026.

### Qué cambia
**1. Informe en PDF para el comité** (crítica 4 del jurado: "el directivo se va sin nada en la mano").
- `ia/resumen.py` (nuevo): informe tamaño carta con la situación actual de la compañía, tabla de escenarios guardados y detalle de cada uno (cifras, solidez de la evidencia, interpretación y diferencias con el resto). No llama a la IA: funciona sin internet. Cada cifra pasa por el validador antes de imprimirse; si alguna no está en los datos, sale "Dato no disponible". El estilo está todo junto en el bloque «Estilo del informe».
- `ui/explicacion.py`: `boton_resumen()`. El PDF se arma antes de dibujar el botón y se guarda en la sesión (evita el error "Deferred file not found" de Streamlit).
- `requirements.txt`: `fpdf2==2.8.9`. Después del pull hay que correr `pip install -r requirements.txt` (o `install.bat`).
- `sandbox/c_resumen.py`, `tests/test_resumen.py`, README.
- El botón aparece en la app cuando Gaby conecte `EXTRAS["resumen"]` en `app.py` (su PR va después de este).

**2. Arreglo: «Explicar» cuando no hay con quién comparar.**
- `ia/plantilla.py`, `ia/explicar.py`: si al bajar una palanca todas las empresas la cumplen (no queda "resto"), la explicación ya no muestra el mensaje de falla: dice que no hay con quién comparar y sugiere un nivel superior. En ese caso no se llama a la IA. Pruebas en `tests/test_sin_comparacion.py`.

### Cómo probarlo
1. `pip install -r requirements.txt` y `pytest -q` → 456 passed, 7 skipped.
2. `streamlit run sandbox/c_resumen.py`: elegir escenarios y descargar el PDF.
3. En la app: COMPAÑIA 29 → aguinaldo a 15 con [−] → Explicar → debe decir que no hay con quién comparar.

Probado: ninguna cifra inventada en los 26 pasos del caché ni en ~1,700 escenarios al azar de las 40 empresas; los 26 tipos de "diferencia con el resto" revisados; descargas en navegador real con recargas en medio, 10 de 10 bien.

Commit de unión: `ba65714`. Archivos que cambiaron (9): `README.md`, `ia/explicar.py`, `ia/plantilla.py`, `ia/resumen.py`, `requirements.txt`, `sandbox/c_resumen.py`, `tests/test_resumen.py`, `tests/test_sin_comparacion.py`, `ui/explicacion.py`.

## PR 29 · docs: guion v5 con el orden elegido por el equipo

Rama `d/e6-guion-v5` · Juan Esteban Acosta (@juanesaacosta26) · abierto el 19/10/2026, unido a `main` el 19/10/2026.

Sin descripción escrita.

Solo cambió documentos internos de la presentación, que no forman parte de esta versión, por eso su commit de unión no aparece en el historial público.

## PR 30 · Completa verificador y plan de contingencia de la demo

Rama `a/e7-usabilidad` · Alejandra Cortés (@AlejaCortes) · abierto el 20/10/2026, unido a `main` el 20/10/2026.

### Qué cambia
verificar_demo.py: comprueba el parquet, el caché, la API de Anthropic, la respuesta y el tiempo del motor, y que app.py se ejecute y Streamlit responda localmente en MODO_DEMO.
contingencia.md con los pasos para fallas de la app, la API o la laptop.

### Cómo probarlo
Ejecutar en la terminal:

python scripts/verificar_demo.py

Verificar que el script realice las comprobaciones previstas y reporte los resultados correspondientes. Ejecutar también ruff check . y pytest para revisar la calidad del código y las pruebas del proyecto

Commit de unión: `8733573`. Archivos que cambiaron (1): `scripts/verificar_demo.py`.

## PR 31 · B/integracion total

Rama `b/integracion_total` · Gabriela Chisaba (@gabriela708) · abierto el 20/10/2026, unido a `main` el 20/10/2026.

### Qué cambia
App final, todas las funcionales agregadas, estilos y uso intuitivo verificado.

### Cómo probarlo
streamlit run app.py (desde terminal)

Commit de unión: `849a16f`. Archivos que cambiaron (5): `app.py`, `sandbox/b_pantalla.py`, `tests/test_pantalla.py`, `ui/comparativo.py`, `ui/tema.py`.

## PR 32 · docs: README de entrega, licencia del equipo y vocabulario nuevo en el PDF y la plantilla

Rama `c/e8-v1` · Julián David Rodríguez (@jdrodriguez03) · abierto el 20/10/2026, unido a `main` el 20/10/2026.

### Qué cambia
Cierra la versión 1.0 para la entrega a Catch y la publicación.
- **README** reescrito para Catch y para el portafolio: descripción, contexto del concurso, características, requisitos, instalación, configuración de la llave de API, uso paso a paso con la pantalla nueva, cómo funciona, estructura, datos, pruebas, equipo y licencia.
- **LICENSE** a nombre de los cuatro integrantes.
- **CODEOWNERS**: el usuario de Aleja pasa de `@alejac-beep` (no existía) a `@AlejaCortes`.
- **CLAUDE.md** sin la fecha de la demo ni la referencia a `docs/proyecto.docx`.
- **PDF para el comité** con el vocabulario nuevo de la pantalla (PR 31): «con / sin la medida» en lugar de «grupo / resto», «Ahorro» en lugar de cifras entre paréntesis y «Costo anual de la brecha».
- **Semáforo**: «de las que no» y «completado con similares» en lugar de «del resto» y «grupo completado».
- **Plantilla**: al bajar una prestación ya no escribe «$-2,547,798 pesos que costaría la medida», sino «la medida representa un ahorro de $2.5 millones de pesos al año», igual que la pantalla.

### Cómo probarlo
`pytest` (469 pasan, 2 omitidas) y `ruff check .`. En la app con `scripts\demo_sin_internet.bat`: COMPAÑIA 36, bajar los vales, Explicar, guardar escenario y descargar el PDF. Ni la explicación ni el PDF muestran signos negativos, y el PDF usa el vocabulario nuevo.

Commit de unión: `088f9fb`. Archivos que cambiaron (12): `.github/CODEOWNERS`, `CLAUDE.md`, `LICENSE`, `README.md`, `ia/plantilla.py`, `ia/resumen.py`, `ia/semaforo.py`, `tests/test_explicacion.py`, `tests/test_plantilla.py`, `tests/test_resumen.py`, `tests/test_semaforo.py`, `ui/explicacion.py`.
