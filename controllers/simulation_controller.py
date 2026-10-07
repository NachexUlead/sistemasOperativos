"""Coordinate input, simulation, reporting, and error handling."""

import sys
from pathlib import Path

from services.process_input import InputError, read_processes
from services.scheduler import simulate
from services.metrics import calculate_metrics
from services.result_output import save_results, save_events
from views.console_view import show_summary


def run_simulation(input_file="procesos.csv", output_directory="."):
    """Execute the application workflow and return its exit status."""
    output = Path(output_directory)
    input_path = Path(input_file).resolve()
    if input_path in {(output / name).resolve() for name in ("resultados.csv", "eventos.txt")}:
        print("Error: the input file cannot be an output file.", file=sys.stderr)
        return 1
    try:
        processes = read_processes(input_file)
        events = simulate(processes)
        metrics = calculate_metrics(processes)
        output.mkdir(parents=True, exist_ok=True)
        save_results(processes, output / "resultados.csv")
        save_events(events, output / "eventos.txt")
    except (InputError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    show_summary(processes, metrics)
    print(f"\nGenerated files: {output / 'resultados.csv'} and {output / 'eventos.txt'}")
    return 0

