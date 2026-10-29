# MiniOS — Programada Dos

Extensión del MiniOS de `programadaUno`, conservando la organización en modelos,
servicios, controladores y vistas. Esta versión agrega Round Robin, respuesta,
expropiaciones, utilización del CPU y cambios de contexto. Programada Uno conserva
su versión original. Requiere Python 3.10 o posterior y solo su biblioteca estándar.

## Ejecutar

Desde `programadaDos`:

```bash
python3 minios.py
python3 minios.py --archivo procesos.csv --politica rr --quantum 3
python3 minios.py --archivo procesos.csv --politica fifo
python3 minios.py --archivo procesos.csv --politica rr --quantum 1 --comparar
```

En Windows puede utilizarse `py` o `python` en lugar de `python3`. No hay que instalar
paquetes. Tampoco se usa `input()`.

La entrada predeterminada es `procesos.csv` junto al programa. Las rutas explícitas
son relativas al directorio desde el cual se ejecuta el comando. Las salidas
`resultados.csv` y `eventos.txt` se escriben en el directorio actual; `--salida carpeta`
permite conservar cada corrida por separado. `--output` es un alias de `--salida`.
`--comparar` muestra FIFO y RR para el mismo archivo y quantum, y conserva en los
archivos la política elegida con `--politica`. Es la opción adicional del enunciado.

La CLI usa RR y quantum 3 por defecto. En FIFO se ignora el quantum; con
`--comparar` se valida porque también se ejecuta RR. Los errores terminan con un
código distinto de cero y sin iniciar la simulación.

## Formato de entrada

```csv
id,llegada,duracion
P1,0,5
P2,2,3
P3,3,8
P4,6,2
```

También se acepta `id,arrival,duration`, el encabezado original de Programada Uno.
Los identificadores deben ser únicos y no vacíos; llegada es un entero no negativo
y duración es un entero positivo. El orden del archivo decide los empates y el
orden de las filas de resultados, aunque las llegadas no estén ordenadas.

## Cómo funciona

- `models/process.py`: estado, tiempo restante, primer inicio, fin y métricas del proceso.
- `services/process_input.py`: lectura y validación de todas las filas antes de simular.
- `services/scheduler.py`: reloj entero y cola `deque`, compartidos por FIFO y RR.
- `services/metrics.py`: métricas globales comunes a las dos políticas.
- `services/result_output.py`: CSV en español y registro de eventos.
- `controllers/simulation_controller.py`: coordina ejecución, archivos y errores.
- `views/console_view.py`: resumen y comparación en pantalla.

En cada instante se admiten primero las llegadas. Después se termina el proceso
actual o se revisa su quantum. Si tiene trabajo pendiente y hay alguien esperando,
vuelve al final de la cola; los recién llegados ya están delante. Si está solo,
renueva quantum sin expropiación ni cambio de contexto. Luego se asigna el CPU y
se ejecuta una unidad. Los cambios no cuestan tiempo; la primera asignación no
cuenta y el último usuario del CPU se conserva incluso durante períodos ociosos.

Para cada proceso: `retorno = fin - llegada`, `espera = retorno - duracion` y
`respuesta = inicio - llegada`. El tiempo de inicio se guarda solo la primera vez.
Utilización = `100 * tiempo_ocupado / tiempo_total`, incluyendo el ocio inicial.
Los empates de mayor y menor espera muestran al primero en el archivo.

## Pruebas

```bash
python3 -m unittest discover -s tests -v
python3 minios.py --archivo casos/un_solo_proceso.csv --quantum 1
python3 minios.py --archivo casos/llegadas_simultaneas.csv --quantum 1
python3 minios.py --archivo casos/desempate_quantum.csv --quantum 2
python3 minios.py --archivo casos/cpu_ocioso.csv --quantum 3
python3 minios.py --archivo procesos.csv --quantum 18 --comparar
python3 minios.py --archivo casos/invalidos/duplicados.csv
```

El último comando debe fallar con un mensaje de identificador duplicado.
También hay archivos inválidos de valores, filas incompletas, archivo vacío y
solo encabezado. Las pruebas comprueban los ejemplos del PDF, FIFO original,
Q=1, Q grande, desempates, finalización al agotar el quantum, ocio, salidas y CLI.
Además verifican conservación de tiempo y espera acumulada en cargas reproducibles.

## Análisis y entrega

El análisis compara FIFO y RR con Q=1, Q=3 y Q=18 sobre `procesos.csv` y sobre
`casos/analisis_ocho_procesos.csv`. Los resultados de cada corrida están bajo
`analisis/`, junto con la tabla `analisis/comparacion.csv` y el informe
`analisis/informe.pdf` de dos páginas. `analisis/informe.md` contiene el texto editable.

Los archivos principales `resultados.csv` y `eventos.txt` corresponden a RR con
quantum 3 sobre `procesos.csv`. La entrega incluye código, módulos, casos,
pruebas, resultados, eventos e informe. Puede comprobarse descomprimiéndola en
otra carpeta y ejecutando los comandos de las secciones anteriores.

## Dos aclaraciones del PDF

1. La sección 19 pide al menos seis procesos para el análisis, pero los entregables
   exigen ocho. Se utilizan ocho para cumplir ambos mínimos.
2. La tabla de la sección 18 indica dos expropiaciones para P3. La regla 9.2.7 dice
   que renovar quantum con la cola vacía no es expropiación. En t=16 P3 está solo:
   esta implementación registra **una** expropiación para P3 y una renovación sin
   expropiación. El resto de los resultados coincide, incluidos los cinco cambios
   de contexto. La prueba correspondiente documenta esta decisión.

## Resultados esperados de la ejecución predeterminada

Tiempo total 18; espera promedio 4.75; retorno promedio 9.25; respuesta promedio
2.25; CPU 100%; cinco cambios de contexto. En la sección 10 (Q=2), las pruebas
comprueban espera 4.67, retorno 8.67, respuesta 1.00 y seis cambios de contexto.
