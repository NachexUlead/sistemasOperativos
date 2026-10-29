"""Non-preemptive FIFO scheduling, one integer time unit per step."""

from collections import deque


def simulate(processes):
    """Advance in integer time units and update process results."""
    if not processes:
        raise ValueError("At least one process is required.")
    # Stable sorting preserves input order for simultaneous arrivals.
    pending = deque(sorted(processes, key=lambda process: process.arrival))
    queue = deque()
    current = None
    time = completed = 0
    events = []

    def record(message):
        events.append(f"[{time}] {message}")

    for process in processes:
        process.reset()

    while completed < len(processes):
        if current is not None and current.remaining == 0:
            current.complete(time)
            record(f"{current.identifier} finishes (Terminated)")
            completed += 1
            current = None
        while pending and pending[0].arrival == time:
            process = pending.popleft()
            record(f"{process.identifier} arrives")
            process.admit()
            queue.append(process)
            record(f"{process.identifier} enters the queue (Ready)")
        if current is None and queue:
            current = queue.popleft()
            current.dispatch(time)
            record(f"{current.identifier} starts execution (Running)")
        if completed == len(processes):
            break
        if current is not None:
            current.execute_tick()
            record(f"{current.identifier} executes [{time},{time + 1}); "
                      f"remaining at the end of the interval: {current.remaining}")
        else:
            record(f"CPU idle [{time},{time + 1})")
        time += 1
    return events

