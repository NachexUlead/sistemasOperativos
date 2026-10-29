"""Archivos de resultados en el orden original de entrada."""

import csv
from pathlib import Path


def save_results(processes, path="resultados.csv"):
    with Path(path).open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["id", "llegada", "duracion", "inicio", "fin", "espera", "retorno",
                         "respuesta", "expropiaciones"])
        for p in processes:
            writer.writerow([p.identifier, p.arrival, p.duration, p.start, p.finish, p.wait,
                             p.turnaround, p.response, p.preemptions])


def save_events(events, path="eventos.txt"):
    Path(path).write_text("\n".join(events) + "\n", encoding="utf-8")
