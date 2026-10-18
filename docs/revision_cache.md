# Revisión del caché

Generado por `scripts/revisar_cache.py`, sin internet. Dueño: Julian.

**26 de 26 pasos sin problemas.**

| # | Guion | Fuente | Segundos | Palabras | Creado | Problemas |
|---|---|---|---|---|---|---|
| 1 | sí | cache | 0.000 | 61 | 2026-10-17 | bien |
| 2 | sí | cache | 0.000 | 66 | 2026-10-17 | bien |
| 3 | sí | cache | 0.000 | 74 | 2026-10-17 | bien |
| 4 | sí | cache | 0.000 | 71 | 2026-10-17 | bien |
| 5 |  | cache | 0.000 | 60 | 2026-10-17 | bien |
| 6 |  | cache | 0.000 | 71 | 2026-10-17 | bien |
| 7 |  | cache | 0.000 | 69 | 2026-10-17 | bien |
| 8 |  | cache | 0.000 | 60 | 2026-10-17 | bien |
| 9 |  | cache | 0.000 | 70 | 2026-10-17 | bien |
| 10 |  | cache | 0.000 | 70 | 2026-10-17 | bien |
| 11 |  | cache | 0.000 | 66 | 2026-10-17 | bien |
| 12 |  | cache | 0.000 | 61 | 2026-10-17 | bien |
| 13 |  | cache | 0.000 | 63 | 2026-10-17 | bien |
| 14 |  | cache | 0.000 | 64 | 2026-10-17 | bien |
| 15 |  | cache | 0.000 | 68 | 2026-10-17 | bien |
| 16 |  | cache | 0.000 | 71 | 2026-10-17 | bien |
| 17 |  | cache | 0.000 | 69 | 2026-10-18 | bien |
| 18 |  | cache | 0.000 | 59 | 2026-10-17 | bien |
| 19 |  | cache | 0.000 | 63 | 2026-10-18 | bien |
| 20 |  | cache | 0.000 | 69 | 2026-10-18 | bien |
| 21 |  | cache | 0.000 | 70 | 2026-10-17 | bien |
| 22 |  | cache | 0.000 | 71 | 2026-10-17 | bien |
| 23 |  | cache | 0.000 | 67 | 2026-10-17 | bien |
| 24 |  | cache | 0.000 | 61 | 2026-10-17 | bien |
| 25 |  | cache | 0.000 | 68 | 2026-10-17 | bien |
| 26 |  | cache | 0.000 | 61 | 2026-10-17 | bien |

## Textos

### 1. `COMPAÑIA 36|aguinaldo_op=20|15000`

Las 22 empresas que ya dan aguinaldo de 20 días o más pierden 22% de su plantilla al año; las otras 16, 53%. Para su empresa, esa diferencia equivale a $6.3 millones de pesos al año en bajas, contra $2.3 millones de pesos que costaría la medida. Además, la mayoría de esas empresas también da prima vacacional de 50% o más.

### 2. `COMPAÑIA 36|aguinaldo_op=20,prima_vac_op=0.5|15000 <- COMPAÑIA 36|aguinaldo_op=20|15000`

Con la prima vacacional de 50%, sumada al aguinaldo de 20 días, quedan 16 empresas, antes 22; pierden 17% de su plantilla al año y las demás, 43%. Para su empresa, la diferencia equivale a $7.4 millones de pesos al año en bajas, contra $3.7 millones de la medida. Además, esas empresas suelen tener un fondo de ahorro con un valor más alto que las demás.

### 3. `COMPAÑIA 36|aguinaldo_op=20,prima_vac_op=0.5,sal_dia_ini=350|15000 <- COMPAÑIA 36|aguinaldo_op=20,prima_vac_op=0.5|15000`

Con el salario inicial de $350, sumado al aguinaldo de 20 días y la prima vacacional de 50%, quedan 5 empresas, antes 16; pierden 12% de su plantilla al año y las otras 33 empresas, 38%. Para su empresa, la diferencia equivale a $8.5 millones de pesos al año en bajas, contra $17.6 millones de pesos que costaría la medida. Con estos datos la señal no es concluyente: tómelo como referencia, no como conclusión.

### 4. `COMPAÑIA 36|aguinaldo_op=20,prima_vac_op=0.5,sal_dia_ini=350|30000 <- COMPAÑIA 36|aguinaldo_op=20,prima_vac_op=0.5,sal_dia_ini=350|15000`

Con el costo por baja en $30,000, la diferencia en bajas equivale a $17.1 millones al año, antes $8.5 millones, contra $17.6 millones que costaría la medida. Las 5 empresas que ya dan aguinaldo de 20 días, prima vacacional de 50% y salario inicial de $350 pierden 12% de su plantilla al año; las 33 restantes, 38%. Con estos datos la señal no es concluyente: tómelo como referencia, no como conclusión.

### 5. `COMPAÑIA 29|prima_vac_op=0.5|15000`

Las 20 empresas que ya dan prima vacacional de 50% o más pierden 20% de su plantilla al año; las otras 18, 43%. Para su empresa, esa diferencia equivale a $5.0 millones de pesos al año en bajas, contra $250 mil pesos que costaría la medida. Con estos datos la señal no es concluyente: tómelo como referencia, no como conclusión.

### 6. `COMPAÑIA 29|prima_vac_op=0.5,rutas_x100=3|15000 <- COMPAÑIA 29|prima_vac_op=0.5|15000`

Con las rutas de 3 por cada 100 operativos, sumadas a la prima vacacional de 50%, quedan 6 empresas, antes 20; pierden 12% de su plantilla al año y las otras 32 empresas, 39%. Para su empresa, esa diferencia equivale a $5.8 millones de pesos al año en bajas, contra $4.7 millones de pesos que costaría la medida. Además, esas empresas suelen tener menos bajas por motivos personales que las demás.

### 7. `COMPAÑIA 15|sal_dia_ini=340|15000`

Las 12 empresas que ya dan un salario inicial de $340 o más pierden 16% de su plantilla al año; las otras 27, 42%. Para su empresa, esa diferencia equivale a $25.9 millones de pesos al año en bajas, contra $8.2 millones de pesos que costaría la medida, un 2.6% de su nómina operativa base. Además, la mayoría de esas empresas también da prima vacacional de 50% o más.

### 8. `COMPAÑIA 15|sal_dia_ini=350|15000 <- COMPAÑIA 15|sal_dia_ini=340|15000`

Con el salario inicial de $350, quedan 7 empresas, antes 12; pierden 12% de su plantilla al año y las otras 32 empresas, 38%. Para su empresa, la diferencia equivale a $27.3 millones de pesos al año en bajas, contra $17.9 millones de pesos de la medida. Además, casi todas esas empresas también dan prima vacacional de 50% o más.

### 9. `COMPAÑIA 36|aguinaldo_op=20,prima_vac_op=0.5|15000`

Las 16 empresas que ya dan aguinaldo de 20 días y prima vacacional de 50% o más pierden 17% de su plantilla al año; las otras 22 empresas, 43%. Para su empresa, esa diferencia equivale a $7.4 millones de pesos al año en bajas, contra $3.7 millones de pesos que costaría la medida. Además, esas empresas suelen tener un fondo de ahorro con un valor más alto que las demás.

### 10. `COMPAÑIA 36|aguinaldo_op=20,prima_vac_op=0.5,sal_dia_ini=350|15000`

Las 5 empresas que ya dan aguinaldo de 20 días, prima vacacional de 50% y salario inicial de $350 o más pierden 12% de su plantilla al año; las otras 33, 38%. Para su empresa, esa diferencia equivale a $8.5 millones de pesos al año en bajas, contra $17.6 millones de pesos que costaría la medida. Con estos datos la señal no es concluyente: tómelo como referencia, no como conclusión.

### 11. `COMPAÑIA 36|sal_dia_ini=340|15000`

Las 12 empresas que ya tienen un salario inicial de $340 o más pierden 16% de su plantilla al año; las otras 27, 42%. Para su empresa, que hoy pierde 52%, esa diferencia equivale a $7.8 millones de pesos al año en bajas, contra $8.6 millones de pesos que costaría la medida. Además, la mayoría de esas empresas también da prima vacacional de 50% o más.

### 12. `COMPAÑIA 36|prima_vac_op=0.5|15000`

Las 20 empresas que ya dan prima vacacional de 50% o más pierden 20% de su plantilla al año; las otras 18, 43%. Para su empresa, esa diferencia equivale a $6.9 millones de pesos al año en bajas, contra $1.4 millones de pesos que costaría la medida. Con estos datos la señal no es concluyente: tómelo como referencia, no como conclusión.

### 13. `COMPAÑIA 36|vales_op=0.1|15000`

Las 19 empresas que ya dan vales de 10% o más pierden 24% de su plantilla al año; las otras 16, 34%. Para su empresa, esa diferencia equivale a $6.0 millones de pesos al año en bajas, contra $1.7 millones de pesos que costaría la medida. Además, esas empresas suelen tener un fondo de ahorro con un valor más alto que las demás.

### 14. `COMPAÑIA 36|rutas_x100=5|15000`

Las 13 empresas que ya dan rutas de 5 por cada 100 operativos o más pierden 13% de su plantilla al año; las otras 25, 38%. Para su empresa, esa diferencia equivale a $8.3 millones de pesos al año en bajas, contra $13.0 millones de pesos que costaría la medida. Con estos datos la señal no es concluyente: tómelo como referencia, no como conclusión.

### 15. `COMPAÑIA 36|aguinaldo_op=20,vales_op=0.1|15000`

Las 14 empresas que ya dan aguinaldo de 20 días o más y vales de 10% o más pierden 15% de su plantilla al año; las otras 21 empresas, 44%. Para su empresa, esa diferencia equivale a $7.9 millones de pesos al año en bajas, contra $4.0 millones de pesos que costaría la medida. Además, la mayoría de esas empresas también da prima vacacional de 50% o más.

### 16. `COMPAÑIA 36|prima_vac_op=0.5,rutas_x100=5|15000`

Las 5 empresas que ya dan prima vacacional de 50% y tienen 5 rutas por cada 100 operativos pierden 12% de su plantilla al año; las otras 33 empresas, 40%. Para su empresa, esa diferencia equivale a $8.5 millones de pesos al año en bajas, contra $14.4 millones de pesos que costaría la medida. Además, esas empresas suelen tener un valor más bajo que las demás en bajas por motivos personales.

### 17. `COMPAÑIA 36|sal_dia_ini=380|15000`

Las 5 empresas que ya dan un salario inicial de $380 o más pierden 10% de su plantilla al año; las otras 34, 39%. Para su empresa, esa diferencia equivale a unas 604 personas al año, o $9.1 millones de pesos en bajas, contra $29.6 millones de pesos que costaría la medida. Como hay pocas empresas con esta combinación, se sumaron otras similares: tómelo como referencia, no como conclusión.

### 18. `COMPAÑIA 36|aguinaldo_op=32|15000`

Las 5 empresas que ya dan aguinaldo de 32 días o más pierden 16% de su plantilla al año; las otras 33, 40%. Para su empresa, esa diferencia equivale a $7.8 millones de pesos al año en bajas, contra $7.9 millones de pesos que costaría la medida. Además, todas esas empresas también dan prima vacacional de 50% o más.

### 19. `COMPAÑIA 36|prima_vac_op=1|15000`

Las 5 empresas que ya dan prima vacacional de 100% pierden 16% de su plantilla al año; las otras 33 empresas, 38%. Para su empresa, esa diferencia equivale a $7.8 millones de pesos al año en bajas, contra $4.2 millones de pesos que costaría la medida. Como hay pocas empresas con esta combinación, se sumaron otras similares: tómelo como referencia, no como conclusión.

### 20. `COMPAÑIA 36|rutas_x100=10.8|15000`

Pocas empresas dan 10.8 rutas por cada 100 operativos o más, por eso el grupo se completó con las más parecidas hasta llegar a 5 empresas: pierden 60% de su plantilla al año; las 33 restantes, 29%. La medida costaría $48 millones al año, y su empresa ya rota menos que esas 5 empresas. Con un grupo completado y una señal no concluyente, tómelo como referencia, no como conclusión.

### 21. `COMPAÑIA 36|vales_op=0.06|15000`

Las 33 empresas que ya dan vales de 6% o más pierden 25% de su plantilla al año; las otras 2 empresas, 59%. Para su empresa, esa diferencia equivale a $5.7 millones de pesos al año en bajas, y la medida no le costaría: bajar los vales le ahorraría unos $5.1 millones de pesos al año. Con estos datos la señal no es concluyente: tómelo como referencia, no como conclusión.

### 22. `COMPAÑIA 29|sal_dia_ini=320|15000`

Las 21 empresas que ya dan un salario inicial de $320 o más pierden 24% de su plantilla al año; las otras 18 empresas, 41%. Para su empresa, esa diferencia equivale a unas 302 personas al año, una diferencia en bajas de $4.5 millones de pesos al año, contra $7.8 millones de pesos que costaría la medida. Con estos datos la señal no es concluyente: tómelo como referencia, no como conclusión.

### 23. `COMPAÑIA 29|prima_vac_op=0.5,rutas_x100=3|15000`

Las 6 empresas que ya dan prima vacacional de 50% y tienen 3 rutas por cada 100 operativos pierden 12% de su plantilla al año; las otras 32 empresas, 39%. Para su empresa, esa diferencia equivale a $5.8 millones de pesos al año en bajas, contra $4.7 millones de pesos que costaría la medida. Además, esas empresas suelen tener menos bajas por motivos personales que las demás.

### 24. `COMPAÑIA 15|vales_op=0.08|15000`

Las 30 empresas que ya dan vales de 8% o más pierden 27% de su plantilla al año; las otras 5 empresas, 38%. Para su empresa, esa diferencia equivale a $21.3 millones de pesos al año en bajas, contra $11.3 millones de pesos que costaría la medida. Con estos datos la señal no es concluyente: tómelo como referencia, no como conclusión.

### 25. `COMPAÑIA 15|rutas_x100=2|15000`

Las 21 empresas que ya tienen rutas de 2 por cada 100 operativos o más pierden 38% de su plantilla al año; las otras 17, 36%. Para su empresa, que hoy pierde 80%, esa diferencia equivale a $16.8 millones de pesos al año en bajas, contra $19.0 millones de pesos que costaría la medida. Con estos datos la señal no es concluyente: tómelo como referencia, no como conclusión.

### 26. `COMPAÑIA 15|sal_dia_ini=350|15000`

Las 7 empresas que ya dan un salario inicial de $350 o más pierden 12% de su plantilla al año; las otras 32, 38%. Para su empresa, esa diferencia equivale a $27.3 millones de pesos al año en bajas, contra $17.9 millones de pesos que costaría la medida. Además, casi todas esas empresas también dan prima vacacional de 50% o más.
