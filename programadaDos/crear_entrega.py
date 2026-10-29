"""Reproduce experimentos, informe PDF de dos páginas y ZIP sin instalar nada."""

import csv
from pathlib import Path
import textwrap
from zipfile import ZipFile, ZIP_DEFLATED

from services.metrics import calculate_metrics
from services.process_input import read_processes
from services.result_output import save_events, save_results
from services.scheduler import simulate


ROOT = Path(__file__).resolve().parent
CONFIGURATIONS = [("fifo", None), ("rr", 1), ("rr", 3), ("rr", 18)]


def run_experiments():
    experiments = {}
    for name, relative_path in (("base", "procesos.csv"),
                                ("ocho_procesos", "casos/analisis_ocho_procesos.csv")):
        measurements = []
        for policy, quantum in CONFIGURATIONS:
            result = simulate(read_processes(ROOT / relative_path), policy, quantum)
            measurements.append(calculate_metrics(result))
            output = ROOT / "analisis" / name / (policy if quantum is None else f"rr_q{quantum}")
            output.mkdir(parents=True, exist_ok=True)
            save_results(result.processes, output / "resultados.csv")
            save_events(result.events, output / "eventos.txt")
        experiments[name] = measurements
    with (ROOT / "analisis/comparacion.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["archivo", "politica", "quantum", "procesos", "tiempo_total", "espera_promedio",
                         "retorno_promedio", "respuesta_promedio", "cambios_contexto", "utilizacion_cpu"])
        for name, measurements in experiments.items():
            for m in measurements:
                writer.writerow([name, m["policy"], m["quantum"], m["count"], m["total_time"],
                                 m["average_wait"], m["average_turnaround"], m["average_response"],
                                 m["context_switches"], m["cpu_utilization"]])
    return experiments


def report_pages(experiments):
    def table(name):
        lines = ["Política   Q    Espera   Retorno   Respuesta   Cambios   CPU útil"]
        for m in experiments[name]:
            lines.append(f"{m['policy'].upper():<8} {str(m['quantum'] or '-'):>3}"
                         f" {m['average_wait']:>9.2f} {m['average_turnaround']:>9.2f}"
                         f" {m['average_response']:>10.2f} {m['context_switches']:>9}"
                         f" {m['cpu_utilization']:>8.1f}%")
        return "\n".join(lines)

    base, own = experiments["base"], experiments["ocho_procesos"]
    base_useful = 100 * base[1]["busy_time"] / (base[1]["total_time"] + base[1]["context_switches"])
    own_useful = 100 * own[1]["busy_time"] / (own[1]["total_time"] + own[1]["context_switches"])
    page1 = [
        "MINIOS: ANÁLISIS COMPARATIVO DE FIFO Y ROUND ROBIN",
        "1. Método y datos",
        "Se ejecutaron FIFO y RR con quantum 1, 3 y 18, con cambios de contexto de costo cero. "
        "Todas las llegadas y duraciones son enteras; las llegadas preceden al proceso expropiado "
        "en caso de empate. La utilización incluye el tiempo desde cero hasta el último fin.",
        "Caso base: procesos.csv; P1=(0,5), P2=(2,3), P3=(3,8), P4=(6,2). "
        "Tiempo total y CPU ocupado: 18 unidades en todas las políticas.",
        table("base"),
        "Caso propio: casos/analisis_ocho_procesos.csv. Pares (llegada,duración): "
        "LargoA=(0,18), CortoA=(1,1), CortoB=(2,2), MedioA=(3,6), CortoC=(5,1), "
        "LargoB=(6,12), CortoD=(8,2), MedioB=(10,5). Tiempo total y CPU ocupado: 47 unidades.",
        table("ocho_procesos"),
        "2. Respuesta y espera",
        "RR con Q=1 logra la menor respuesta promedio en ambos archivos: 0.75 y 1.625. "
        "La menor espera es FIFO (también RR con Q=18) en el caso base: 4.50; en el caso "
        "propio es RR con Q=1: 12.25. Dar CPU pronto mide respuesta; terminar pronto sin "
        "muchas esperas posteriores determina la espera total. Por eso los mínimos pueden diferir.",
        "Espera = fin - llegada - duración; retorno = fin - llegada; respuesta = inicio - llegada. "
        "Con FIFO, espera y respuesta coinciden; en RR, se suman también las esperas entre turnos.",
        "Las tablas redondean a dos decimales; comparacion.csv conserva mayor precisión. "
        "Las ocho ejecuciones guardan sus propios resultados.csv y eventos.txt bajo analisis/.",
    ]
    page2 = [
        "MINIOS: DISCUSIÓN Y DECISIONES",
        "3. Quantum y cambios de contexto",
        "Con Q=1 se observan 12 cambios en el caso base y 43 en el propio; con Q=3 se reducen "
        "a 5 y 17. Con Q=18 son 3 y 7, los mismos que FIFO, porque ningún proceso necesita "
        "más de un quantum. Un quantum pequeño mejora el acceso inicial al CPU, pero "
        "aumenta los cambios entre procesos cuando hay competencia.",
        "4. Efecto convoy",
        "En el caso propio, LargoA ocupa el CPU de 0 a 18 bajo FIFO. CortoA llega en 1 y "
        "solo necesita una unidad, pero espera 17 para empezar y termina en 19. Con RR Q=1 "
        "empieza en 1 y termina en 2; con Q=3 empieza en 3 y termina en 4. Este proceso "
        "concreto muestra el convoy detrás de la tarea larga.",
        "5. Si cada cambio costara una unidad",
        f"Como estimación conservando las secuencias observadas, con Q=1 la utilización útil "
        f"sería 18/(18+12) = {base_useful:.2f}% y 47/(47+43) = {own_useful:.2f}%. "
        "El CPU puede estar ocupado cambiando de contexto sin avanzar trabajo útil. Si se "
        "simulara ese costo, las llegadas durante los cambios podrían alterar la secuencia "
        "y el número de cambios; estas cifras son una aproximación, no otra simulación.",
        "6. Quantum recomendado",
        "Para un sistema compartido elegiría Q=3 como compromiso: en el caso propio baja "
        "la respuesta de 20.00 a 5.00 y la espera de 20.00 a 12.875 frente a FIFO, con 17 "
        "cambios en lugar de 43 con Q=1. Si la prioridad absoluta fuera responder cuanto "
        "antes y los cambios realmente fueran gratis, Q=1 sería preferible en estos datos. "
        "La recomendación depende del objetivo y no se generaliza a cualquier carga.",
        "7. Verificación y aclaración del enunciado",
        "Las pruebas automatizadas reproducen las secciones 10 y 18, FIFO y los casos de "
        "desempate, ocio, llegadas simultáneas, renovación sin competencia y entradas inválidas. "
        "El conjunto propio tiene ocho procesos, cumpliendo el mínimo más estricto de los entregables.",
        "La tabla de la sección 18 asigna dos expropiaciones a P3. Según la regla 9.2.7, "
        "en t=16 P3 está solo y renueva su quantum sin expropiación: el resultado correcto "
        "siguiendo esa regla es una expropiación. Se conservan los otros valores de la tabla, "
        "incluidos los cinco cambios de contexto. No se cuenta la primera asignación.",
    ]
    return [page1, page2]


def save_pdf(pages, path):
    """PDF sencillo con fuentes integradas; no requiere paquetes ni conversores.

    Cada elemento es un párrafo; las tablas conservan sus saltos de línea.
    Se comprueba que el texto cabe en las dos páginas A4.
    """
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b"", b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>"]
    page_ids = []
    for number, paragraphs in enumerate(pages, 1):
        lines = []
        for paragraph in paragraphs:
            for line in paragraph.splitlines():
                lines.extend(textwrap.wrap(line, width=82, replace_whitespace=False, drop_whitespace=True) or [""])
            lines.append("")
        if len(lines) > 55:
            raise ValueError(f"La página {number} excede el espacio disponible ({len(lines)} líneas).")
        commands = [b"BT /F1 10 Tf 13 TL 48 794 Td"]
        for line in lines:
            escaped = line.encode("cp1252").replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
            commands.append(b"(" + escaped + b") Tj T*")
        commands.extend([b"ET", f"BT /F1 9 Tf 48 35 Td (MiniOS - {number}/2) Tj ET".encode()])
        content = b"\n".join(commands)
        page_id, stream_id = len(objects) + 1, len(objects) + 2
        page_ids.append(page_id)
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> /Contents {stream_id} 0 R >>".encode())
        objects.append(f"<< /Length {len(content)} >>\nstream\n".encode() + content + b"\nendstream")
    objects[1] = f"<< /Type /Pages /Count {len(pages)} /Kids [{' '.join(f'{i} 0 R' for i in page_ids)}] >>".encode()
    document = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(document))
        document.extend(f"{i} 0 obj\n".encode() + obj + b"\nendobj\n")
    start_xref = len(document)
    document.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        document.extend(f"{offset:010d} 00000 n \n".encode())
    document.extend(f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{start_xref}\n%%EOF\n".encode())
    path.write_bytes(document)


def create_archive():
    destination = ROOT / "entrega_programada_dos.zip"
    # Lista explícita: solo materiales de la solución y sus evidencias.
    files = [ROOT / name for name in ("minios.py", "procesos.csv", "resultados.csv", "eventos.txt",
                                      "README.md")]
    for directory in ("models", "services", "controllers", "views", "tests", "casos", "analisis"):
        files.extend(p for p in (ROOT / directory).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, path.relative_to(ROOT))
    return destination


def main():
    experiments = run_experiments()
    pages = report_pages(experiments)
    (ROOT / "analisis/informe.md").write_text(
        "\n\n---\n\n".join("\n\n".join(page) for page in pages) + "\n", encoding="utf-8")
    save_pdf(pages, ROOT / "analisis/informe.pdf")
    result = simulate(read_processes(ROOT / "procesos.csv"), "rr", 3)
    save_results(result.processes, ROOT / "resultados.csv")
    save_events(result.events, ROOT / "eventos.txt")
    print(f"Informe de dos páginas: {ROOT / 'analisis/informe.pdf'}")
    print(f"Entrega: {create_archive()}")


if __name__ == "__main__":
    main()
