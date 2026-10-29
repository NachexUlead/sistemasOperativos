"""Coordina lectura, simulación, métricas y salida, como en la Tarea 1."""

from copy import deepcopy
from pathlib import Path
import sys

from services.metrics import calculate_metrics
from services.process_input import InputError, read_processes
from services.result_output import save_events, save_results
from services.scheduler import simulate
from views.console_view import show_comparison, show_summary


def run_simulation(input_file="procesos.csv", policy="rr", quantum=3,
                   output_directory=".", compare=False):
    output = Path(output_directory)
    if Path(input_file).resolve() in {(output / name).resolve()
                                     for name in ("resultados.csv", "eventos.txt")}:
        print("Error: el archivo de entrada no puede ser uno de los archivos de salida.", file=sys.stderr)
        return 1
    try:
        processes = read_processes(input_file)
        result = simulate(processes, policy, quantum)
        metrics = calculate_metrics(result)
        comparison = []
        if compare:
            # Copias independientes: cada resultado conserva sus propios procesos.
            for comparison_policy in ("fifo", "rr"):
                comparison.append(calculate_metrics(simulate(deepcopy(processes), comparison_policy, quantum)))
        output.mkdir(parents=True, exist_ok=True)
        save_results(processes, output / "resultados.csv")
        save_events(result.events, output / "eventos.txt")
    except (InputError, ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    show_summary(processes, metrics)
    if compare:
        show_comparison(comparison)
    print(f"\nArchivos generados: {output / 'resultados.csv'} y {output / 'eventos.txt'}")
    return 0
