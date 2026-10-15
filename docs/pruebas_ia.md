# Pruebas de la explicación de la IA

Julian · 9 de octubre · sandbox/c_explicacion.py con "API real"

Cada texto se generó con el fixture indicado y su paso anterior. Revisión: máximo 3 oraciones, menciona el número de empresas, sin palabras prohibidas, cifras iguales al JSON.

## Comparación de modelos (paso 01)

| Modelo | Primera palabra | Palabras | Resultado |
|---|---|---|---|
| claude-haiku-4-5-20251001 | 0.66 s | 56 | Bien. Retiro agendado no antes del 15 de octubre de 2026 |
| claude-haiku-5-5 | 0.71 s | 86 | Se alarga y menciona palancas que no se movieron |
| claude-sonnet-5-5 | 0.69 s | 60 | Bien. Elegido |

Los modelos 5.5 piensan antes de escribir por defecto: sin apagarlo, la primera palabra pasaba de 4 s y caía a la plantilla. ia/explicar.py lo apaga (Sonnet: between_tools; Haiku: disabled).

## Arreglos al prompt y al mensaje que salieron de estas pruebas

| Problema observado | Arreglo |
|---|---|
| Con varias palancas movidas nombraba solo la última ("16 empresas con esa medida") | El prompt pide nombrar cada palanca de palancas_movidas, con un ejemplo de frase |
| Decía "todas tienen un salario más alto" cuando el dato era una mediana | `como_decirlo` en ia/prompts.py calcula en código "la mayoría", "suelen tener un valor más alto", etc. |
| Usaba un rasgo obvio ("todas dan prima de 50%" cuando la prima era la palanca movida) | `rasgos_utiles` quita los rasgos de palancas movidas y se manda solo uno |
| Comparaba el paso 01 con el estado inicial ("antes 39") | Un paso anterior sin cambio se trata como primera comparación |
| Escribía "$0.0 millones" cuando la empresa ya pierde menos | `nota_pesos` le da la frase lista y el prompt pide usar el porcentaje de la empresa |
| Usaba "reduce", "en su sector" y "promedio" | Reglas nuevas en el prompt; el sandbox las marca como prohibidas |

## Textos con claude-sonnet-5-5

### 01 · Aguinaldo 15 → 20 (sin paso anterior)

Las 22 empresas que ya dan 20 días de aguinaldo o más pierden 22% de su plantilla al año; las demás, 53%. Para su empresa, que hoy pierde 52%, esa diferencia equivale a $6.3 millones de pesos al año en bajas, contra $2.3 millones de pesos que costaría la medida. Además, la mayoría de esas empresas también da prima vacacional de 50% o más.

- 64 palabras · 0.71 s · ya no compara con el estado inicial ("antes 39").

### 02 · + Prima 25% → 50% (anterior: 01)

Con la prima vacacional de 50% y el aguinaldo de 20 días, quedan 16 empresas, antes 22; pierden 17% de su plantilla al año y las demás, 43%. Para su empresa, que hoy pierde 52%, la diferencia equivale a $7.4 millones de pesos al año en bajas, contra $3.7 millones de la medida. Además, esas empresas suelen tener un salario inicial más alto, aunque la señal es débil.

- 68 palabras · 0.92 s · cifras y reglas bien.

### 03 · + Salario → $350 (anterior: 02)

Con el salario inicial de $350 diarios, la prima vacacional de 50% y el aguinaldo de 20 días, quedan 5 empresas, antes 16; pierden 12% de su plantilla al año y las demás, 38%. Para su empresa, la diferencia equivale a $8.5 millones de pesos al año en bajas, contra $17.6 millones de la medida. Con solo 5 empresas, la señal no es concluyente, así que conviene tomar esta comparación con cautela.

- 72 palabras · 0.70 s · cifras bien, advierte que no es concluyente.

### 04 · Vales, ya pierde menos (COMPAÑIA 37)

Las 7 empresas que ya dan vales de 12% o más pierden 42% de su plantilla al año; las demás, 34%. Para su empresa, que hoy pierde 4% al año, no hay diferencia en pesos a su favor frente a esas empresas, así que no se compara con el costo de la medida. Además, esas empresas tienen un salario inicial parecido al de las demás, y con tan pocas empresas la señal no es concluyente.

- 75 palabras · 0.70 s · la nota de pesos funcionó. "con tan pocas empresas" es una deducción suya (la señal es no concluyente por p = 0.68).

### 05 · Estado inicial

Hoy su empresa pierde 52% de su plantilla al año, mientras que las 39 empresas de la encuesta pierden 36%, sin que haya movido ninguna medida. Esa diferencia equivale a $3.4 millones de pesos al año en bajas, y como aún no hay medida, no hay costo que comparar. Mueva una palanca, como aguinaldo, prima vacacional o salario inicial, para ver qué muestran las empresas que ya la aplican.

- 69 palabras · 1.09 s · ya no dice "promedio".

## Respaldo

Con "API lenta", la plantilla sale a los 4.01 s con fuente "plantilla" y sin errores en pantalla.

## Días 7 y 8 · 15 estados reales del motor

Julian · 14 de octubre · `python scripts/probar_ia.py` con claude-sonnet-5-5

Los 15 casos salen de `scripts/combinaciones.yaml` y se calculan con `motor.api.calcular_estado`, igual que en la app. G2 y G3 se explican con el paso anterior (G1 y G2); los demás, como primera comparación. Cada texto se revisa con el validador (cifras) y con `ia/reglas.py` (forma). Los textos completos, con su estado, quedan en `docs/textos_ia.json`, y `tests/test_reglas_ia.py` los vuelve a revisar en cada PR sin llamar a la IA.

**Resultado final: 15 de 15 cumplen todas las reglas, y los 15 saldrían de la IA en vivo.**

| Caso | Qué cubre | Palabras | Segundos |
|---|---|---|---|
| G1 | Guion 1 · aguinaldo a 20, señal clara | 61 | 2.1 |
| G2 | Guion 2 · + prima 50%, señal débil, "antes 22" | 65 | 1.7 |
| G3 | Guion 3 · + salario $350, no concluyente | 74 | 1.9 |
| S1 | Salario a $340 | 62 | 1.7 |
| S2 | Prima a 50% (no concluyente con 20 empresas) | 61 | 1.7 |
| S3 | Vales a 10% | 63 | 1.8 |
| S4 | Rutas a 5 | 64 | 1.9 |
| D1 | Aguinaldo + vales | 65 | 1.7 |
| D2 | Prima + rutas (5 empresas, señal clara) | 70 | 1.8 |
| E1 | Salario a $380 · grupo completado | 65 | 1.7 |
| E3 | Prima a 100% · grupo completado | 62 | 1.7 |
| E5 | Vales **bajados** a 6% · resto de 2 · la medida ahorra | 71 | 1.8 |
| R29-1 | COMPAÑIA 29 · medida de $250 mil | 60 | 1.6 |
| R15-1 | COMPAÑIA 15 · resto de 5 | 60 | 2.5 |
| R15-3 | COMPAÑIA 15 · montos de $27.3 millones | 61 | 1.7 |

### Primera corrida: 12 de 15, y lo que encontramos

| Problema | Ejemplo | Arreglo |
|---|---|---|
| Con señal no concluyente, la IA juntaba aviso y rasgo y pasaba de 75 palabras (G3, E5, R15-1) | "la señal es no concluyente, **así que** esas empresas suelen citar menos el horario…" | Con aviso no se manda el rasgo (`_para_ia`) |
| Cada texto inventaba su advertencia y explicaba por qué | "Con **solo 20** empresas…", "Con tan pocas empresas…" | Aviso escrito en el JSON (`aviso_senal`), como `nota_pesos`; "así que", "tan pocas" y "con solo" prohibidas |
| "0 de 5" se nombraba "pocas" | G3: jornadas de 12 horas | `como_decirlo`: 0 → "ninguna" |
| La jerga del motor llegaba al texto | "fondo de ahorro **mediano**" | `nombre_rasgo` quita "mediano/a" |
| Montos de menos de un millón | "$0.3 millones" (R29-1) | Se escriben en miles ("$250 mil"); el validador acepta esa forma |
| Palabras pegadas | "$14.4millones", "lamedida" | `pulir()` separa número o coma pegados a una letra, y restaura el aviso exacto si se pegó |
| Resto muy chico presentado como grupo | E5: "las demás, 59%" con 2 empresas | `nota_resto`: "las otras 2 empresas" |

### Lo que salió en el camino

- **La temperatura no se puede configurar.** La guía pedía temperatura baja, pero `anthropic==1.11.0` ya no acepta `temperature`: mandarla lanzaba un error y **todas** las explicaciones caían a la plantilla sin que se notara en pantalla. Se quitó, y `test_no_manda_temperatura` evita que vuelva. La consistencia la dan los arreglos de arriba: aviso escrito, rasgo calculado en código y `pulir()`.
- **Un costo negativo es un ahorro.** En E5 (vales bajados) la medida "cuesta" −$5.1 millones; la IA escribe "le ahorraría $5.1 millones". El validador ahora acepta la cifra en positivo.
- **Tiempos agotados: 2 en unas 30 llamadas, ambos a los 8 s.** `_cliente_real()` corta la conexión a los 8 s (el doble del límite de 4 s). En vivo sale la plantilla, que es lo diseñado, pero cerca de 1 de cada 15 pulsaciones podría salir de ella sin que nada falle. **Pendiente para el día 11:** el precálculo del caché quiere esperar hasta 15 s y hoy igual se corta a los 8 s.
- **Para el caché del día 11:** con el botón Explicar, además del guion paso a paso, conviene guardar el salto aguinaldo → prima + salario de un solo golpe (un juez puede mover dos palancas sin pulsar).

