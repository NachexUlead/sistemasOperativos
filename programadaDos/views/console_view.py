"""Tablas legibles en español sin dependencias externas."""


def show_table(rows):
    rows = [[str(value) for value in row] for row in rows]
    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    for row in rows:
        print("  ".join(value.ljust(width) for value, width in zip(row, widths)))


def show_summary(processes, metrics):
    policy = "FIFO" if metrics["policy"] == "fifo" else f"Round Robin (quantum = {metrics['quantum']})"
    print(f"\nRESULTADO MINIOS\nPolítica: {policy}\n{'=' * 65}")
    rows = [["Proceso", "Llegada", "Duración", "Inicio", "Fin", "Espera", "Retorno",
             "Respuesta", "Expropiaciones"]]
    rows.extend([p.identifier, p.arrival, p.duration, p.start, p.finish, p.wait, p.turnaround,
                 p.response, p.preemptions] for p in processes)
    show_table(rows)
    print(f"\nProcesos ejecutados: {metrics['count']}")
    print(f"Tiempo total: {metrics['total_time']}")
    print(f"Espera promedio: {metrics['average_wait']:.2f}")
    print(f"Retorno promedio: {metrics['average_turnaround']:.2f}")
    print(f"Respuesta promedio: {metrics['average_response']:.2f}")
    print(f"Mayor espera: {metrics['longest_wait_process']} ({metrics['longest_wait']})")
    print(f"Menor espera: {metrics['shortest_wait_process']} ({metrics['shortest_wait']})")
    print(f"Utilización del CPU: {metrics['cpu_utilization']:.1f}%")
    print(f"Cambios de contexto: {metrics['context_switches']}")


def show_comparison(metrics_list):
    print("\nCOMPARACIÓN DE POLÍTICAS")
    rows = [["Política", "Quantum", "Espera", "Retorno", "Respuesta", "Cambios", "CPU"]]
    for m in metrics_list:
        rows.append([m["policy"].upper(), m["quantum"] or "—", f"{m['average_wait']:.2f}",
                     f"{m['average_turnaround']:.2f}", f"{m['average_response']:.2f}",
                     m["context_switches"], f"{m['cpu_utilization']:.1f}%"])
    show_table(rows)
