"""Datos y transiciones de los procesos de MiniOS, extendidos de la Tarea 1."""

from dataclasses import dataclass, field


@dataclass
class Process:
    identifier: str
    arrival: int
    duration: int
    state: str = field(default="Nuevo", init=False)
    remaining: int = field(init=False)
    start: int | None = field(default=None, init=False)
    finish: int | None = field(default=None, init=False)
    wait: int | None = field(default=None, init=False)
    turnaround: int | None = field(default=None, init=False)
    response: int | None = field(default=None, init=False)
    preemptions: int = field(default=0, init=False)

    def __post_init__(self):
        if not self.identifier.strip():
            raise ValueError("El identificador no puede estar vacío.")
        if type(self.arrival) is not int or self.arrival < 0:
            raise ValueError("La llegada debe ser un entero mayor o igual que cero.")
        if type(self.duration) is not int or self.duration <= 0:
            raise ValueError("La duración debe ser un entero mayor que cero.")
        self.reset()

    def reset(self):
        self.state = "Nuevo"
        self.remaining = self.duration
        self.start = self.finish = self.wait = self.turnaround = self.response = None
        self.preemptions = 0

    def admit(self):
        self.state = "Listo"

    def dispatch(self, time):
        self.state = "Ejecutando"
        if self.start is None:
            self.start = time

    def execute_tick(self):
        self.remaining -= 1

    def preempt(self):
        self.preemptions += 1
        self.state = "Listo"

    def complete(self, time):
        self.state = "Terminado"
        self.finish = time
        self.turnaround = self.finish - self.arrival
        self.wait = self.turnaround - self.duration
        self.response = self.start - self.arrival
