MINIOS: ANÁLISIS COMPARATIVO DE FIFO Y ROUND ROBIN

1. Método y datos

Se ejecutaron FIFO y RR con quantum 1, 3 y 18, con cambios de contexto de costo cero. Todas las llegadas y duraciones son enteras; las llegadas preceden al proceso expropiado en caso de empate. La utilización incluye el tiempo desde cero hasta el último fin.

Caso base: procesos.csv; P1=(0,5), P2=(2,3), P3=(3,8), P4=(6,2). Tiempo total y CPU ocupado: 18 unidades en todas las políticas.

Política   Q    Espera   Retorno   Respuesta   Cambios   CPU útil
FIFO       -      4.50      9.00       4.50         3    100.0%
RR         1      5.75     10.25       0.75        12    100.0%
RR         3      4.75      9.25       2.25         5    100.0%
RR        18      4.50      9.00       4.50         3    100.0%

Caso propio: casos/analisis_ocho_procesos.csv. Pares (llegada,duración): LargoA=(0,18), CortoA=(1,1), CortoB=(2,2), MedioA=(3,6), CortoC=(5,1), LargoB=(6,12), CortoD=(8,2), MedioB=(10,5). Tiempo total y CPU ocupado: 47 unidades.

Política   Q    Espera   Retorno   Respuesta   Cambios   CPU útil
FIFO       -     20.00     25.88      20.00         7    100.0%
RR         1     12.25     18.12       1.62        43    100.0%
RR         3     12.88     18.75       5.00        17    100.0%
RR        18     20.00     25.88      20.00         7    100.0%

2. Respuesta y espera

RR con Q=1 logra la menor respuesta promedio en ambos archivos: 0.75 y 1.625. La menor espera es FIFO (también RR con Q=18) en el caso base: 4.50; en el caso propio es RR con Q=1: 12.25. Dar CPU pronto mide respuesta; terminar pronto sin muchas esperas posteriores determina la espera total. Por eso los mínimos pueden diferir.

Espera = fin - llegada - duración; retorno = fin - llegada; respuesta = inicio - llegada. Con FIFO, espera y respuesta coinciden; en RR, se suman también las esperas entre turnos.

Las tablas redondean a dos decimales; comparacion.csv conserva mayor precisión. Las ocho ejecuciones guardan sus propios resultados.csv y eventos.txt bajo analisis/.

---

MINIOS: DISCUSIÓN Y DECISIONES

3. Quantum y cambios de contexto

Con Q=1 se observan 12 cambios en el caso base y 43 en el propio; con Q=3 se reducen a 5 y 17. Con Q=18 son 3 y 7, los mismos que FIFO, porque ningún proceso necesita más de un quantum. Un quantum pequeño mejora el acceso inicial al CPU, pero aumenta los cambios entre procesos cuando hay competencia.

4. Efecto convoy

En el caso propio, LargoA ocupa el CPU de 0 a 18 bajo FIFO. CortoA llega en 1 y solo necesita una unidad, pero espera 17 para empezar y termina en 19. Con RR Q=1 empieza en 1 y termina en 2; con Q=3 empieza en 3 y termina en 4. Este proceso concreto muestra el convoy detrás de la tarea larga.

5. Si cada cambio costara una unidad

Como estimación conservando las secuencias observadas, con Q=1 la utilización útil sería 18/(18+12) = 60.00% y 47/(47+43) = 52.22%. El CPU puede estar ocupado cambiando de contexto sin avanzar trabajo útil. Si se simulara ese costo, las llegadas durante los cambios podrían alterar la secuencia y el número de cambios; estas cifras son una aproximación, no otra simulación.

6. Quantum recomendado

Para un sistema compartido elegiría Q=3 como compromiso: en el caso propio baja la respuesta de 20.00 a 5.00 y la espera de 20.00 a 12.875 frente a FIFO, con 17 cambios en lugar de 43 con Q=1. Si la prioridad absoluta fuera responder cuanto antes y los cambios realmente fueran gratis, Q=1 sería preferible en estos datos. La recomendación depende del objetivo y no se generaliza a cualquier carga.

7. Verificación y aclaración del enunciado

Las pruebas automatizadas reproducen las secciones 10 y 18, FIFO y los casos de desempate, ocio, llegadas simultáneas, renovación sin competencia y entradas inválidas. El conjunto propio tiene ocho procesos, cumpliendo el mínimo más estricto de los entregables.

La tabla de la sección 18 asigna dos expropiaciones a P3. Según la regla 9.2.7, en t=16 P3 está solo y renueva su quantum sin expropiación: el resultado correcto siguiendo esa regla es una expropiación. Se conservan los otros valores de la tabla, incluidos los cinco cambios de contexto. No se cuenta la primera asignación.
