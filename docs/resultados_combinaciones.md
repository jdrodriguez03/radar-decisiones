# Resultados de las 20 combinaciones

Generado por scripts/correr_combinaciones.py el 2026-10-10. Costo por baja: $15,000; costo mensual por ruta: $35,000.

**Resumen:** 20 casos corridos, 4 con alerta, 3 con grupo completado.

## Tabla

| Caso | Empresa | Palancas movidas | n grupo | n resto | Rot. empresa | Rot. grupo | Rot. resto | Señal | Completado | Costo medida | Costo brecha | Alertas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G1 | COMPAÑIA 36 | aguinaldo_op=20 | 22 | 16 | 52% | 22% | 53% | clara | no | $2.3 M | $6.3 M | — |
| G2 | COMPAÑIA 36 | aguinaldo_op=20, prima_vac_op=0.5 | 16 | 22 | 52% | 17% | 43% | débil | no | $3.7 M | $7.4 M | — |
| G3 | COMPAÑIA 36 | aguinaldo_op=20, prima_vac_op=0.5, sal_dia_ini=350 | 5 | 33 | 52% | 12% | 38% | no concluyente | no | $17.6 M | $8.5 M | — |
| S1 | COMPAÑIA 36 | sal_dia_ini=340 | 12 | 27 | 52% | 16% | 42% | débil | no | $8.6 M | $7.8 M | — |
| S2 | COMPAÑIA 36 | prima_vac_op=0.5 | 20 | 18 | 52% | 20% | 43% | no concluyente | no | $1.4 M | $6.9 M | — |
| S3 | COMPAÑIA 36 | vales_op=0.1 | 19 | 16 | 52% | 24% | 34% | débil | no | $1.7 M | $6.0 M | — |
| S4 | COMPAÑIA 36 | rutas_x100=5 | 13 | 25 | 52% | 13% | 38% | no concluyente | no | $13.0 M | $8.3 M | — |
| D1 | COMPAÑIA 36 | aguinaldo_op=20, vales_op=0.1 | 14 | 21 | 52% | 15% | 44% | clara | no | $4.0 M | $7.9 M | — |
| D2 | COMPAÑIA 36 | prima_vac_op=0.5, rutas_x100=5 | 5 | 33 | 52% | 12% | 40% | clara | no | $14.4 M | $8.5 M | — |
| E1 | COMPAÑIA 36 | sal_dia_ini=380 | 5 | 34 | 52% | 38% | 32% | no concluyente | sí | $29.6 M | $2.8 M | el grupo rota más que el resto |
| E2 | COMPAÑIA 36 | aguinaldo_op=32 | 5 | 33 | 52% | 16% | 40% | débil | no | $7.9 M | $7.8 M | — |
| E3 | COMPAÑIA 36 | prima_vac_op=1.0 | 5 | 33 | 52% | 20% | 38% | no concluyente | sí | $4.2 M | $6.7 M | — |
| E4 | COMPAÑIA 36 | rutas_x100=10.8 | 5 | 33 | 52% | 49% | 36% | no concluyente | sí | $48.0 M | $518 mil | el grupo rota más que el resto |
| E5 | COMPAÑIA 36 | vales_op=0.06 | 33 | 2 | 52% | 25% | 59% | no concluyente | no | −$5.1 M | $5.7 M | resto con menos de 5 |
| R29-1 | COMPAÑIA 29 | prima_vac_op=0.5 | 20 | 18 | 66% | 20% | 43% | no concluyente | no | $250 mil | $5.0 M | — |
| R29-2 | COMPAÑIA 29 | sal_dia_ini=320 | 21 | 18 | 66% | 24% | 41% | no concluyente | no | $7.8 M | $4.5 M | — |
| R29-3 | COMPAÑIA 29 | prima_vac_op=0.5, rutas_x100=3 | 6 | 32 | 66% | 12% | 39% | clara | no | $4.7 M | $5.8 M | — |
| R15-1 | COMPAÑIA 15 | vales_op=0.08 | 30 | 5 | 80% | 27% | 38% | no concluyente | no | $11.3 M | $21.3 M | — |
| R15-2 | COMPAÑIA 15 | rutas_x100=2 | 21 | 17 | 80% | 38% | 36% | no concluyente | no | $19.0 M | $16.8 M | el grupo rota más que el resto |
| R15-3 | COMPAÑIA 15 | sal_dia_ini=350 | 7 | 32 | 80% | 12% | 38% | débil | no | $17.9 M | $27.3 M | — |

## Revisión de los pasos del guion

- **G1** (Guion paso 1: aguinaldo de 15 a 20 días): coincide
- **G2** (Guion paso 2: además, prima vacacional a 50%): coincide
- **G3** (Guion paso 3: además, salario inicial a $350): coincide

## Casos con alerta

- **E1** · Salario inicial al máximo ($380): el grupo rota más que el resto (grupo 38% contra resto 32%, n = 5 vs 34).
- **E4** · Rutas al máximo (10.8 por cada 100): el grupo rota más que el resto (grupo 49% contra resto 36%, n = 5 vs 33).
- **E5** · Vales al mínimo (6%), por debajo del valor real: resto con menos de 5 (grupo 25% contra resto 59%, n = 33 vs 2).
- **R15-2** · COMPAÑIA 15: rutas a 2 por cada 100: el grupo rota más que el resto (grupo 38% contra resto 36%, n = 21 vs 17).
