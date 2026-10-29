"""Present simulation results in the terminal."""

def show_summary(processes, metrics):
    print("\n===============================\n       MINIOS RESULTS\n===============================")
    rows = [["Process", "Arrival", "Duration", "Start", "Finish", "Wait", "Turnaround"]]
    rows.extend([[str(value) for value in (p.identifier, p.arrival, p.duration,
                                          p.start, p.finish, p.wait, p.turnaround)] for p in processes])
    widths = [max(len(row[i]) for row in rows) for i in range(7)]
    for row in rows:
        print("  ".join(value.ljust(width) for value, width in zip(row, widths)))
    print(f"\nProcesses executed: {metrics['count']}")
    print(f"Total time: {metrics['total_time']}")
    print(f"Average wait: {metrics['average_wait']:.2f}")
    print(f"Average turnaround: {metrics['average_turnaround']:.2f}")
    print(f"Longest wait: {', '.join(metrics['longest_wait_processes'])} ({metrics['longest_wait']})")
    print(f"Shortest wait: {', '.join(metrics['shortest_wait_processes'])} ({metrics['shortest_wait']})")

