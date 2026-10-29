"""Write simulation results and event logs."""

import csv
from pathlib import Path


def save_results(processes, path="resultados.csv"):
    with Path(path).open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "arrival", "duration", "start", "finish", "wait", "turnaround"])
        for p in processes:
            writer.writerow([p.identifier, p.arrival, p.duration, p.start, p.finish, p.wait, p.turnaround])


def save_events(events, path="eventos.txt"):
    Path(path).write_text("\n".join(events) + "\n", encoding="utf-8")


