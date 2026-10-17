# Anomalías de las 20 combinaciones

Dueño: Juanes (persona D) · Bloque 4, día 7 · Fuente: `docs/resultados_combinaciones.md`,
generado por `scripts/correr_combinaciones.py` con el motor real (`motor.api.calcular_estado`),
costo por baja $15,000 y costo mensual por ruta $35,000.

**Para qué sirve este documento:** antes de la demo queremos conocer cada resultado raro que
un juez podría provocar moviendo los controles, entender por qué pasa y tener lista una
respuesta de una o dos frases. Un resultado raro explicado con calma da confianza; uno que
nos sorprende en vivo la quita.

## Resumen

- Los 3 pasos del guion **coinciden** con el motor real: 22/16 con 22% contra 53% (señal clara,
  p = 0.047); 16/22 con 17% contra 43% (débil, p = 0.051); 5/33 con 12% contra 38%
  (no concluyente, p = 0.235). Pesos: $2.3 M / $6.3 M, $3.7 M / $7.4 M, $17.6 M / $8.5 M.
- **4 casos con alerta** (E1, E4, E5, R15-2) y **3 vigilados** sin alerta (E3, R15-1, E2).
- **2 problemas para Aleja** que conviene resolver antes del día 8: cómo se completa el grupo
  y la COMPAÑIA 27 (plantilla 0).
- Los 5 fixtures se regeneraron con el motor real y siguen cumpliendo su papel; ninguno cambió
  de cifras clave, salvo el 05, que ahora sí trae los ids de las 39 empresas del grupo.

## Casos con alerta

| Caso | Qué hace el juez | Qué aparece | Por qué pasa | Cómo se explica en la demo |
|---|---|---|---|---|
| **E1** | Salario inicial al máximo ($380) | Grupo completado de 5 · rota **más** que el resto (38% contra 32%) · no concluyente · medida $29.6 M | Solo 2 empresas pagan $380 o más (COMPAÑIA 19 y 27). El motor completa a 5 con las más parecidas, pero en la salida actual **esas 2 no quedan en el grupo** (ver Problema 1). | "Casi nadie paga tanto; la herramienta completó el grupo y lo avisa. Con 5 empresas y señal no concluyente, no hay evidencia para pagar $29.6 M." |
| **E4** | Rutas al máximo (10.8 por cada 100) | Grupo completado de 5 · rota más (49% contra 36%) · no concluyente · medida $48 M | Solo 2 empresas tienen tantas rutas (COMPAÑIA 11 y 16) y son plantas chicas; las 5 del grupo tienen menos de 210 operativos y una rota 180%. | "Las empresas con tantas rutas son plantas chicas que no se parecen a una de 1,438 operativos. Por eso la herramienta lo marca como no concluyente." |
| **E5** | Baja los vales a 6% (por debajo de su 9% real) | Grupo de 33 y resto de **2** · medida **negativa** (−$5.1 M) · no concluyente | El nivel es un mínimo: "6% o más" incluye a casi todas. Solo COMPAÑIA 13 y 15 dan menos. La medida es negativa porque bajar una prestación ahorra. | "Bajar los vales ahorra $5.1 M, pero casi nadie da tan poco, así que no hay con quién comparar." |
| **R15-2** | Con COMPAÑIA 15, rutas a 2 | Grupo de 21 que rota apenas más que el resto (38% contra 36%) · no concluyente (p = 0.93) | Es ruido: 2 puntos de diferencia con p = 0.93 es como lanzar una moneda. | "Para esta empresa las rutas no marcan diferencia, y la herramienta lo dice claro." Mejor no usar este caso en la demo. |

## Casos vigilados (sin alerta, pero un juez podría preguntar)

| Caso | Qué aparece | Qué vigilar | Cómo se explica |
|---|---|---|---|
| **E3** · prima al 100% | Grupo completado de 5 · 20% contra 38% · no concluyente | Hay 4 empresas que cumplen, pero el grupo completado deja fuera a COMPAÑIA 2 (prima de 150%) e incluye a COMPAÑIA 4, con **8 operativos** y 180% de rotación. | "Solo 4 empresas dan el 100%; completamos con la más parecida y la señal no es concluyente." |
| **R15-1** · COMPAÑIA 15, vales a 8% | Grupo de 30 y resto de **exactamente 5** | No salta la alerta (la regla es "menos de 5"), pero el resto es tan chico que cualquier cifra del resto es frágil. | Igual que E5: "casi todas dan 8% o más". |
| **E2** · aguinaldo a 32 días | Grupo de exactamente 5, sin completar · débil | Mezcla plantas de 64 y de 1,439 operativos. | "Son 5 empresas reales; la señal es débil, así que se toma como pista, no como prueba." |
| **S2** contra **G2** · prima a 50% | Sola: 20 empresas, 20% contra 43%, **no concluyente**. Después del aguinaldo: débil. | Un juez puede notar que la misma prima da otra señal. | "La señal depende de con quién se compara: la diferencia se ve grande, pero las empresas varían mucho entre sí." |

## Problemas para Aleja (motor)

**Problema 1 · El grupo completado puede dejar fuera a quien sí cumple.** En E1 las únicas
empresas con salario de $380 o más son COMPAÑIA 19 ($449) y COMPAÑIA 27 ($633), pero el grupo
completado queda con COMPAÑIA 2, 9, 13, 28 y 40: ninguna paga $380. Pasa porque el completado
reemplaza el grupo por las 5 más cercanas al nivel elegido, y las que están muy por encima
quedan "lejos". Lo mismo en E3 (sale COMPAÑIA 2) y E4 (sale COMPAÑIA 11).

- Si el completado **conserva a las que cumplen** y solo agrega las que faltan, E1 cambia mucho:
  grupo 10% contra resto 39%, señal clara (p = 0.022), y deja de ser anomalía. E3 y E4 casi no cambian.
- El documento del proyecto dice "se completa con las más parecidas … hasta llegar a 5", que se lee
  como agregar, no reemplazar. **Decisión para el cierre del día 8:** ¿conservar o reemplazar?

**Problema 2 · COMPAÑIA 27 tiene plantilla 0.** Paga $633 diarios (el doble que la mediana),
no tiene dato en las otras 4 palancas y aparece en el grupo de cualquier movimiento de salario
(por ejemplo, en S1 es 1 de las 12). Con la regla de conservar, sería la mitad de las empresas
"reales" de E1. Propuesta: excluirla del universo en `preparar_datos.py` o en el motor, y
anotarlo en `docs/calidad_datos.md`. Hay que confirmarlo con la empresa dueña de los datos.

**Observación · E4 con "solo empresas de tamaño parecido" no mejora.** El guion v1 sugería
activar esa opción en E4. Con la opción encendida no hay plantas grandes con 10.8 rutas, el grupo
se completa con 5 grandes y queda 66% contra 20% (débil). Conclusión: **no** sugerirla en E4.

## Cambios que esto pide al guion (para la v2 del día 11)

- Sección 2 del guion: quitar la sugerencia de "solo empresas de tamaño parecido" en E4.
- Si se decide conservar a las que cumplen (Problema 1), actualizar E1: deja de ser un caso
  contraintuitivo.
- Quitar R15-2 de las opciones de respaldo: es ruido y no ayuda a contar una historia.

## Cómo se regenera

```
python scripts/correr_combinaciones.py   # tabla nueva en docs/resultados_combinaciones.md
python scripts/regenerar_fixtures.py     # fixtures con la salida real del motor
pytest tests/test_combinaciones.py tests/test_fixtures.py tests/test_fixtures_reales.py
```

Si cambia el motor, se corren los tres comandos y se revisa este documento contra la tabla nueva.