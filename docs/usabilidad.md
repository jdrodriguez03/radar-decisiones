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
| P2 |  |  |  |

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
<!-- fricciones:fin -->

---

## 4. ¿Entendieron lo importante?

Se marca con lo que **dijeron** en la tarea T2 y en las preguntas finales.

| Mensaje que la demo debe transmitir | P1 | P2 |
|---|---|---|
| Las cifras vienen de **empresas reales** que ya dan ese aguinaldo |  |  |
| Es una **comparación**, no una predicción |  |  |
| El grupo (22 empresas) rota **menos** que el resto (22% contra 53%) |  |  |
| La medida cuesta **menos** que la brecha ($2.3 M contra $6.3 M) |  |  |
| El costo por baja es un **supuesto** que el directivo puede cambiar |  |  |

Si un mensaje no lo entendió ninguno de los dos, se agrega como fricción **grave** en la sección 3.

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