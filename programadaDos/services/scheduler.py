"""FIFO y Round Robin con un CPU y cambios de contexto de costo cero."""

from collections import deque
from dataclasses import dataclass


@dataclass
class SimulationResult:
    processes: list
    events: list[str]
    policy: str
    quantum: int | None
    total_time: int
    busy_time: int
    context_switches: int


def simulate(processes, policy="rr", quantum=3):
    """Actualiza los procesos y devuelve el registro y las métricas del CPU.

    En cada frontera de tiempo: llegadas, terminación o vencimiento del
    quantum, asignación y ejecución de [tiempo, tiempo + 1).
    Las llegadas se admiten antes de reencolar al proceso expropiado.
    """
    if policy not in ("fifo", "rr"):
        raise ValueError("La política debe ser 'fifo' o 'rr'.")
    if policy == "rr" and (type(quantum) is not int or quantum <= 0):
        raise ValueError("El quantum debe ser un entero mayor que cero para Round Robin.")
    if not processes:
        raise ValueError("Se necesita al menos un proceso.")
    if len({p.identifier for p in processes}) != len(processes):
        raise ValueError("Los identificadores deben ser únicos.")
    for process in processes:
        process.reset()
    # sorted es estable: conserva el orden del CSV si coinciden las llegadas.
    pending = deque(sorted(processes, key=lambda p: p.arrival))
    ready = deque()
    current = None
    last_identifier = None
    time = completed = used_quantum = busy_time = context_switches = 0
    events = []

    def record(message):
        events.append(f"[{time}] {message}")

    while completed < len(processes):
        while pending and pending[0].arrival == time:
            process = pending.popleft()
            process.admit()
            ready.append(process)
            record(f"{process.identifier} llega al sistema y entra a la cola (Listo)")

        if current is not None:
            if current.remaining == 0:
                current.complete(time)
                record(f"{current.identifier} termina (Terminado)")
                completed += 1
                current = None
            elif policy == "rr" and used_quantum == quantum:
                if ready:
                    record(f"{current.identifier} agota su quantum (restante={current.remaining})")
                    current.preempt()
                    ready.append(current)
                    record(f"{current.identifier} vuelve a la cola (Listo)")
                    current = None
                else:
                    record(f"{current.identifier} renueva quantum sin expropiación; cola vacía")
                used_quantum = 0

        if current is None and ready:
            current = ready.popleft()
            if last_identifier is not None and last_identifier != current.identifier:
                context_switches += 1
            last_identifier = current.identifier
            action = "inicia" if current.start is None else "retoma"
            current.dispatch(time)
            used_quantum = 0
            record(f"{current.identifier} {action} ejecución (Ejecutando)")

        if completed == len(processes):
            break
        if current is None:
            record(f"CPU ocioso [{time},{time + 1})")
        else:
            current.execute_tick()
            busy_time += 1
            used_quantum += 1
            record(f"{current.identifier} ejecuta [{time},{time + 1}); restante={current.remaining}")
        time += 1

    return SimulationResult(processes, events, policy, quantum if policy == "rr" else None,
                            time, busy_time, context_switches)


def simulate_fifo(processes):
    return simulate(processes, policy="fifo")


def simulate_round_robin(processes, quantum=3):
    return simulate(processes, policy="rr", quantum=quantum)
