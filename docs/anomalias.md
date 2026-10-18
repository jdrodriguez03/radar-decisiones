# Anomalías de las 20 combinaciones

Dueño: Juanes (persona D) · Bloque 4, día 7 · **Actualizado el día 11 (18 de octubre) con el motor
nuevo de Aleja.** Fuente: `docs/resultados_combinaciones.md`, generado por
`scripts/correr_combinaciones.py` con el motor real (`motor.api.calcular_estado`), costo por baja
$15,000 y costo mensual por ruta $35,000.

**Para qué sirve este documento:** antes de la demo queremos conocer cada resultado raro que
un juez podría provocar moviendo los controles, entender por qué pasa y tener lista una
respuesta de una o dos frases. Un resultado raro explicado con calma da confianza; uno que
nos sorprende en vivo la quita.

## Resumen

- Los 3 pasos del guion **no cambiaron** con el motor nuevo: 22/16 con 22% contra 53% (señal clara,
  p = 0.047); 16/22 con 17% contra 43% (débil, p = 0.051); 5/33 con 12% contra 38%
  (no concluyente, p = 0.235). Pesos: $2.3 M / $6.3 M, $3.7 M / $7.4 M, $17.6 M / $8.5 M.
- **Qué cambió:** el grupo completado ahora **conserva a las empresas que sí cumplen** y solo agrega
  las más parecidas hasta llegar a 5 (antes las reemplazaba). Eso movió los tres casos con grupo
  completado: **E1, E3 y E4**. Los otros 17 casos dan exactamente lo mismo que el día 7.
- **3 casos con alerta** (E4, E5, R15-2) y **4 vigilados** sin alerta (E1, E3, R15-1, E2).
  E1 dejó de ser alerta: ahora el grupo rota **menos**.
- **Problema 1 resuelto** (el completado dejaba fuera a quien cumplía). **Problema 2 sigue abierto**
  (COMPAÑIA 27 con plantilla 0) y ahora pesa más, porque está dentro del grupo de E1.

### Qué cambió, caso por caso

| Caso | Antes (día 7) | Ahora (día 11) | Por qué |
|---|---|---|---|
| **E1** · salario a $380 | 38% contra 32% · no concluyente · brecha $2.8 M · alerta | **10% contra 39% · clara (p = 0.022)** · brecha $9.1 M · sin alerta | Ahora quedan dentro COMPAÑIA 19 y 27, que pagan $380 o más y casi no rotan |
| **E3** · prima al 100% | 20% contra 38% · brecha $6.7 M | **16% contra 38%** · brecha $7.8 M | Ahora queda dentro COMPAÑIA 2 (prima de 150%) |
| **E4** · rutas a 10.8 | 49% contra 36% · brecha $518 mil | **60% contra 29%** · **brecha $0** | Ahora quedan dentro COMPAÑIA 11 y 16; la 16 rota 180% |

## Casos con alerta

| Caso | Qué hace el juez | Qué aparece | Por qué pasa | Cómo se explica en la demo |
|---|---|---|---|---|
| **E4** | Rutas al máximo (10.8 por cada 100) | Grupo completado de 5 · rota **más** que el resto (60% contra 29%) · no concluyente (p = 0.188) · medida $48 M · **brecha $0** | Solo 2 empresas tienen 10.8 rutas o más (COMPAÑIA 11 y 16) y se completó con 3 parecidas. Las 5 son plantas chicas (menos de 210 operativos) y una rota 180%. La brecha es **$0** porque COMPAÑIA 36 (52%) ya rota menos que ese grupo (60%): no hay diferencia que cerrar. | "Las empresas con tantas rutas son plantas chicas que rotan más que usted, así que no hay brecha que cerrar y la medida costaría 48 millones. La herramienta lo marca en rojo: rotan más." |
| **E5** | Baja los vales a 6% (por debajo de su 9% real) | Grupo de 33 y resto de **2** · medida **negativa** (−$5.1 M) · no concluyente | El nivel es un mínimo: "6% o más" incluye a casi todas. Solo COMPAÑIA 13 y 15 dan menos. La medida es negativa porque bajar una prestación ahorra. | "Bajar los vales ahorra $5.1 M, pero casi nadie da tan poco, así que no hay con quién comparar." |
| **R15-2** | Con COMPAÑIA 15, rutas a 2 | Grupo de 21 que rota apenas más que el resto (38% contra 36%) · no concluyente (p = 0.93) | Es ruido: 2 puntos de diferencia con p = 0.93 es como lanzar una moneda. | "Para esta empresa las rutas no marcan diferencia, y la herramienta lo dice claro." Mejor no usar este caso en la demo. |

## Casos vigilados (sin alerta, pero un juez podría preguntar)

| Caso | Qué aparece | Qué vigilar | Cómo se explica |
|---|---|---|---|
| **E1** · salario a $380 | Grupo **completado** de 5 · 10% contra 39% · **clara** (p = 0.022) · medida $29.6 M · brecha $9.1 M | **Señal clara y grupo completado a la vez.** Solo 2 empresas pagan $380 o más (COMPAÑIA 19 y 27); las otras 3 pagan entre $367 y $375. Una de las 2 reales es COMPAÑIA 27, con plantilla 0 (Problema 2). El semáforo pone la solidez en naranja porque el grupo se completó, aunque la prueba diga "clara". | "Solo 2 empresas pagan tanto, así que la herramienta completó con las más parecidas y lo avisa. Y aunque rotan menos, la medida cuesta 29.6 millones contra 9.1 de la brecha: con estos datos no se justifica." |
| **E3** · prima al 100% | Grupo completado de 5 · 16% contra 38% · no concluyente | Ahora el grupo incluye a COMPAÑIA 2 (prima de 150%), pero sigue incluyendo a COMPAÑIA 4, con **8 operativos** y 180% de rotación. | "Solo 4 empresas dan el 100%; completamos con la más parecida y la señal no es concluyente." |
| **R15-1** · COMPAÑIA 15, vales a 8% | Grupo de 30 y resto de **exactamente 5** | No salta la alerta (la regla es "menos de 5"), pero el resto es tan chico que cualquier cifra del resto es frágil. | Igual que E5: "casi todas dan 8% o más". |
| **E2** · aguinaldo a 32 días | Grupo de exactamente 5, sin completar · débil | Mezcla plantas de 64 y de 1,439 operativos. | "Son 5 empresas reales; la señal es débil, así que se toma como pista, no como prueba." |
| **S2** contra **G2** · prima a 50% | Sola: 20 empresas, 20% contra 43%, **no concluyente**. Después del aguinaldo: débil. | Un juez puede notar que la misma prima da otra señal. | "La señal depende de con quién se compara: la diferencia se ve grande, pero las empresas varían mucho entre sí." |

## Problemas para Aleja (motor)

**Problema 1 · El grupo completado dejaba fuera a quien sí cumplía. Resuelto en el motor nuevo.**
El completado ahora conserva a las empresas que cumplen y solo agrega las que faltan. Comprobado el
día 11: en E1 quedan COMPAÑIA 19 y 27; en E3, COMPAÑIA 2; en E4, COMPAÑIA 11 y 16.

**Problema 2 · COMPAÑIA 27 tiene plantilla 0. Sigue abierto.** Paga $633 diarios (el doble que la
mediana), no tiene dato en las otras 4 palancas y aparece en el grupo de cualquier movimiento de
salario. Con el motor nuevo pesa más: es **1 de las 2 empresas reales** del grupo de E1, y su
rotación de 1% ayuda a que E1 salga con señal clara. Propuesta: excluirla del universo en
`preparar_datos.py` o en el motor, y anotarlo en `docs/calidad_datos.md`. Hay que confirmarlo con
la empresa dueña de los datos. **Si se excluye, E1 cambia otra vez** y hay que regenerar esta tabla.

**Observación · E4 con "solo empresas de tamaño parecido" no mejora.** Con la opción encendida no
hay plantas grandes con 10.8 rutas y el grupo se completa con 5 grandes. Conclusión: **no**
sugerirla en E4. (Este dato es del día 7; no se volvió a medir con el motor nuevo.)

## Cambios que esto pidió al guion (hechos en la v2 del día 11)

- Sección 2 del guion: E1 y E4 con las cifras nuevas; E1 pasa a ser un caso de "decir que no" por
  costo, no un caso contraintuitivo.
- Sección 2 del guion: se quitó la sugerencia de "solo empresas de tamaño parecido" en E4.
- R15-2 queda solo en "No hacer con COMPAÑIA 15": es ruido y no ayuda a contar una historia.
- `tests/test_guion.py` ahora también revisa las cifras de E1, E4 y E5 (`PASOS_ALERTA`).

## Cómo se regenera

```
python scripts/correr_combinaciones.py   # tabla nueva en docs/resultados_combinaciones.md
python scripts/regenerar_fixtures.py     # fixtures con la salida real del motor
pytest tests/test_combinaciones.py tests/test_fixtures.py tests/test_fixtures_reales.py tests/test_guion.py
```

Si cambia el motor, se corren los tres comandos y se revisa este documento contra la tabla nueva.
