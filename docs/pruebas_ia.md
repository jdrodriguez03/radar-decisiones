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

## Pendientes para el día 7 (afinar el prompt)

- Los textos quedan en 64 a 75 palabras aunque el prompt pida 60: decidir el límite real (el sandbox acepta hasta 75).
- en_comun trae rasgos de palancas ya movidas (16 de 16): hoy se filtran en ia/prompts.py; lo ideal es que el motor no los mande (Aleja, bloque 3).
- La plantilla de respaldo usa "rotar como ese grupo", que el prompt prohíbe.
- Cambio de modelo a claude-sonnet-5-5: avisar al equipo (costo aprox. $0.004 por explicación).
