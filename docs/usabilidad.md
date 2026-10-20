# Prueba con usuarios · día 10

Dueño: Juanes (persona D) · bloque 5.
Se probó la app de **main** (etiqueta e4) con 2 personas ajenas al equipo, sin explicarles nada.
Este documento lo usa Gaby el día 12 para corregir fricciones, empezando por las más graves.

**Regla de oro:** aquí se anota lo que la persona **hizo y dijo**, no lo que creemos que pensó.
"Buscó el ⚙ durante 40 segundos" sirve; "no le gustó el diseño" no sirve.

`tests/test_usabilidad.py` revisa la tabla de la sección 3: que cada fricción tenga dueño,
gravedad válida y que estén ordenadas de más grave a menos grave.

---

## 1. Cómo se hizo (protocolo)

### Antes de empezar (10 min por persona)

- [ ] La app abierta en la pantalla de inicio, **sin** empresa elegida y **sin** palancas movidas.
- [ ] Wifi encendido (la prueba es de entendimiento, no de respaldo sin internet).
- [ ] Esta hoja impresa o abierta en otro equipo; cronómetro a la mano.
- [ ] Nadie del equipo junto a la pantalla, salvo quien conduce. Quien conduce se sienta a un lado, **no** enfrente.

### Lo que dice quien conduce (leerlo tal cual)

> "Gracias por ayudarnos. Vamos a probar una herramienta, no a ti: si algo no se entiende, es culpa
> de la herramienta. Te voy a pedir tres cosas. Mientras las haces, di en voz alta lo que piensas,
> lo que buscas y lo que te sorprende. Yo no te voy a poder ayudar, pero sí voy a tomar nota."

### Las tres tareas

Se dicen una por una. No se mencionan nombres de botones ni de partes de la pantalla.

| # | Lo que se le pide | Termina cuando | Tiempo de referencia |
|---|---|---|---|
| T1 | "Imagina que diriges la COMPAÑIA 36. Ábrela." | COMPAÑIA 36 aparece con 52% de rotación | 30 s |
| T2 | "Sube el aguinaldo de tus operativos. Luego dime con tus palabras qué te dice la pantalla." | Aguinaldo en 20 o más y la persona explicó lo que ve | 1 min para subirlo |
| T3 | "Tu área de RH dice que cada persona que se va les cuesta 30 mil pesos, no 15 mil. Cámbialo." | Costo por baja en $30,000 y la brecha se duplicó (de $6.3 M a $12.7 M si solo subió el aguinaldo a 20) | 1 min |

### Reglas para quien conduce

- **No ayudar.** Si pregunta "¿aquí?", se responde "¿qué harías si yo no estuviera?".
- **Si se atora más de 2 minutos** en una tarea: se da la pista mínima ("está en la parte de las cifras"),
  se anota como **bloqueante** y se pasa a la siguiente.
- **No corregir lo que entendió mal.** Si dice "o sea que mi empresa va a rotar 22%", no se corrige: se anota
  textual. Al final, si quiere, se le explica.
- Anotar el **minuto** de cada tropiezo, lo que **dijo textual** entre comillas y **en qué parte de la pantalla** estaba.

### Preguntas al terminar (3 min)

1. "Si fueras el director de esa empresa, ¿qué decidirías con lo que viste?"
2. "¿Hubo algo que te confundió o que esperabas encontrar y no estaba?"
3. "¿Esta herramienta te dice lo que va a pasar en tu empresa?" (respuesta correcta: no; solo compara)

---

## 2. Participantes

Solo el perfil, sin nombres (el repositorio lo ven todos).

| Clave | Perfil (sin nombre) | ¿Usa Excel o tableros en su trabajo? | Fecha y duración |
|---|---|---|---|
| P1 | Asistente de gerencia para una empresa de publicidad | Si, frecuentemente | 18/10/26 -  |
| P2 | Por completar | Por completar | Por completar |

**Cómo se recogieron las notas:** lo que está abajo viene de lo que cada persona comentó y de lo que se
observó durante la prueba. No se anotaron el minuto exacto ni todas las frases textuales; la única frase
textual es la de P2 sobre la situación actual. Si quien condujo recuerda el minuto o la frase exacta de
algún tropiezo, se agrega en la columna «Qué pasó». Falta completar la duración de P1 y el perfil de P2.

---

## 3. Fricciones (ordenadas de más grave a menos grave)

### Cómo se califica la gravedad

| Gravedad | Cuándo se usa | Ejemplo |
|---|---|---|
| bloqueante | No pudo terminar la tarea sin pista | No encontró dónde cambiar el costo por baja |
| grave | Terminó la tarea pero **entendió algo equivocado** | Creyó que la app predice: "mi empresa va a bajar a 22%" |
| moderada | Terminó y entendió, pero dudó, buscó o tardó más del tiempo de referencia | Movió el slider dos veces porque no vio que la cifra cambió |
| leve | Comentario de forma que no le impidió nada | "La letra de la gráfica es chica" |

"Grave" va por encima de "moderada" a propósito: que el jurado **entienda mal** (por ejemplo, que
piense que predecimos) es peor para la demo que tardarse unos segundos.

### Quién es dueño de cada parte de la pantalla

| Si el problema está en… | Dueño | Archivo |
|---|---|---|
| Elegir empresa o "Mi empresa" | Juanes | ui/selector.py |
| Palancas, botones [−] [+], slider, Restablecer | Gaby | ui/controles.py |
| Las 3 cifras, el encabezado "Comparando con N", la gráfica | Gaby | ui/comparativo.py |
| Letra, colores, contraste, acomodo general | Gaby | ui/tema.py, app.py |
| El panel ⚙ (costo por baja, costo por ruta) | Juanes | ui/supuestos.py |
| Colores de observado / calculado / supuesto | Juanes | ui/procedencia.py |
| Historial de cambios | Juanes | ui/historial.py |
| El texto de la explicación, la señal, palabras raras de la IA | Julian | ui/explicacion.py, ia/ |
| Una cifra que está mal o un cálculo lento | Aleja | motor/ |
| Escenarios A y B | Aleja | ui/escenarios.py |

### La lista

Una fricción por renglón. Columna **Gravedad**: una de `bloqueante`, `grave`, `moderada`, `leve`.
Columna **Dueño**: uno de `Aleja`, `Gaby`, `Julian`, `Juanes`. Si dos personas tropezaron en lo mismo,
es **un solo renglón** con `P1, P2` (y eso la hace más urgente dentro de su gravedad: ponla primero).

<!-- fricciones:inicio -->
| # | Gravedad | Tarea | Dónde (parte de la pantalla) | Qué pasó (hechos y frase textual) | Quién | Dueño | Arreglo propuesto |
|---|---|---|---|---|---|---|---|
| 1 | grave | T3 | Botón ⚙ de supuestos | Las dos personas dijeron que no es evidente que en ese botón se modifican los supuestos. P1 además lo confundió con el semáforo y no entendió bien para qué sirve. | P1, P2 | Juanes | Que el botón diga con palabras «⚙ Supuestos» y, junto a la brecha, la línea fija en ámbar «Supuesto: $15,000 por baja · editable en ⚙» (ya planeada para el día 13, crítica 3). |
| 2 | grave | T2 | Semáforo de evidencia (señal) | P1 necesitó que le explicaran qué significan las señales (clara, débil, no concluyente) para entender lo que veía. | P1 | Julian | Debajo de la barra, una línea fija que diga qué mide: «Qué tan sólida es la comparación: clara, débil o no concluyente». |
| 3 | grave | T2 | Las dos cifras en pesos (centro) | P1 dijo que no le quedó claro qué son el costo anual de la brecha y el costo anual de la medida. | P1 | Gaby | Etiquetas en palabras de negocio: «Lo que cuesta la medida al año» y «Lo que cuesta rotar más que el grupo, al año». |
| 4 | grave | Exploración libre | Costo de la medida (centro) | P2 dijo que no entiende por qué el costo de la medida sale con precio negativo (pasa cuando se baja una palanca por debajo de su valor real, como en el caso E5). | P2 | Gaby | Si el costo sale negativo, mostrarlo como «Ahorro de $5.1 M al año» en lugar de «−$5.1 M». |
| 5 | leve | T1 | Encabezado de la empresa | P2 dijo que entendió bien la pantalla, pero sugirió: «Sería bueno que se viera el número de operadores por empresa y que se aclare la situación actual». | P2 | Gaby | Un recuadro «Situación actual» arriba: operativos, rotación anual frente a la típica de las 40 y los valores reales de las palancas (por ejemplo, 1,438 operativos · 52% contra 37% · aguinaldo 15 días · prima 25%). |
<!-- fricciones:fin -->

---

## 4. ¿Entendieron lo importante?

Se marca con lo que **dijeron** en la tarea T2 y en las preguntas finales.

| Mensaje que la demo debe transmitir | P1 | P2 |
|---|---|---|
| Las cifras vienen de **empresas reales** que ya dan ese aguinaldo | Sin dato | Sin dato |
| Es una **comparación**, no una predicción | Sin dato | Sin dato |
| El grupo (22 empresas) rota **menos** que el resto (22% contra 53%) | Sin dato | Sí (dijo que la pantalla se entiende bien) |
| La medida cuesta **menos** que la brecha ($2.3 M contra $6.3 M) | **No** (no le quedaron claras las dos cifras en pesos) | Parcial (no entendió el costo negativo) |
| El costo por baja es un **supuesto** que el directivo puede cambiar | **No** (confundió el botón ⚙ con el semáforo) | Parcial (dijo que el botón no deja ver que ahí están los supuestos) |

«Sin dato» significa que la persona no lo comentó y nadie se lo preguntó; no quiere decir que no lo
entendió. Para la próxima prueba conviene hacer siempre las tres preguntas finales.

**Los dos mensajes de negocio no los entendió del todo ninguna de las dos personas:** que la medida
cuesta menos que la brecha y que el costo por baja es un supuesto editable. Por eso las fricciones 1,
3 y 4 son **graves**: la regla de esta sección dice que un mensaje que nadie entendió se anota como
grave.

Si un mensaje no lo entendió ninguno de los dos, se agrega como fricción **grave** en la sección 3.

---

## 4.1 Resumen y qué se corrige primero

**Lo que funcionó:** P2 entendió la pantalla en general y dijo que todo estaba claro. La forma de la
pantalla no es el problema.

**Lo que no funcionó:** las tres cosas que hacen útil la herramienta para un directivo no se entienden
solas:

1. **Que los supuestos se pueden cambiar** (fricción 1, las dos personas). Es la más urgente porque le
   pasó a las dos y porque el jurado va a ver el cambio del costo por baja en el video.
2. **Qué significa la señal** (fricción 2). Sin eso, «débil» y «no concluyente» no dicen nada.
3. **Qué son las dos cifras en pesos y por qué una puede ser negativa** (fricciones 3 y 4). Son el
   argumento de negocio de toda la presentación.

**Qué se puede corregir sin romper el congelamiento:** las fricciones 1 a 4 son correcciones de texto
en pantalla (etiquetas y una línea de ayuda), no funciones nuevas. La 5 (recuadro de situación actual)
sí agrega un elemento; si no da tiempo, se cubre en la presentación, porque Juanes y Aleja ya dicen los
operativos y la rotación de la empresa en los bloques 1 y 2 del guion.

**Qué cambia en la presentación mientras se corrigen:** en el bloque 3 del guion, Gaby explica las tres
partes de la pantalla. Conviene que diga con claridad qué significa la etiqueta de evidencia y qué son
las dos cifras en pesos, porque es justo lo que estas personas no entendieron solas.

---

## 5. Qué observar (hipótesis del equipo, NO resultados)

Riesgos que ya sospechamos. Sirven para mirar con atención, **no** para anotarlos si no pasan.

- ¿Encuentran el ⚙? Es un ícono pequeño y la tarea T3 depende de él.
- ¿Entienden palabras como "señal clara", "brecha", "grupo completado" o "n"?
- ¿Dicen algo como "voy a rotar 22%"? Eso es leerlo como predicción.
- ¿Notan el color ámbar del supuesto y que la brecha cambió al cambiarlo?
- ¿Usan los botones [+] o el slider? ¿Ven que las cifras cambiaron después de mover?
- ¿Abren el historial (está cerrado) o ni lo ven?

---

## Anexo · hoja de notas para imprimir (una por persona)

```
Participante: P__     Inicio: __:__     Fin: __:__

T1 · Abrir COMPAÑIA 36            ¿terminó?  sí / con pista / no     tiempo: ____
  Tropiezos (minuto · dónde · frase textual):


T2 · Subir aguinaldo y explicar   ¿terminó?  sí / con pista / no     tiempo: ____
  Lo que dijo que entendió (textual):


  Tropiezos:


T3 · Costo por baja a $30,000     ¿terminó?  sí / con pista / no     tiempo: ____
  Tropiezos:


Preguntas finales
  1. ¿Qué decidirías?
  2. ¿Qué te confundió?
  3. ¿La herramienta predice?   dijo: sí / no / no sabe
```