"""Per-simulation aggregate metrics."""

from statistics import mean


def calculate_metrics(processes):
    waits = [process.wait for process in processes]
    longest, shortest = max(waits), min(waits)
    return {
        "count": len(processes),
        "total_time": max(process.finish for process in processes),
        "average_wait": mean(waits),
        "average_turnaround": mean(process.turnaround for process in processes),
        "longest_wait": longest,
        "shortest_wait": shortest,
        "longest_wait_processes": [p.identifier for p in processes if p.wait == longest],
        "shortest_wait_processes": [p.identifier for p in processes if p.wait == shortest],
    }


