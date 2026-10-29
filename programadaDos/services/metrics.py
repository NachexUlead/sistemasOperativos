"""Métricas comunes a ambas políticas; empates resueltos por orden del CSV."""

from statistics import mean


def calculate_metrics(result):
    processes = result.processes
    longest = max(processes, key=lambda p: p.wait)
    shortest = min(processes, key=lambda p: p.wait)
    return {
        "policy": result.policy,
        "quantum": result.quantum,
        "count": len(processes),
        "total_time": result.total_time,
        "busy_time": result.busy_time,
        "average_wait": mean(p.wait for p in processes),
        "average_turnaround": mean(p.turnaround for p in processes),
        "average_response": mean(p.response for p in processes),
        "longest_wait": longest.wait,
        "longest_wait_process": longest.identifier,
        "shortest_wait": shortest.wait,
        "shortest_wait_process": shortest.identifier,
        "cpu_utilization": 100 * result.busy_time / result.total_time,
        "context_switches": result.context_switches,
    }
