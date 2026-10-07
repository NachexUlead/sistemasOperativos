"""Process data and lifecycle transitions."""

from dataclasses import dataclass, field


@dataclass
class Process:
    identifier: str
    arrival: int
    duration: int
    state: str = field(default="New", init=False)
    remaining: int = field(init=False)
    start: int | None = field(default=None, init=False)
    finish: int | None = field(default=None, init=False)
    wait: int | None = field(default=None, init=False)
    turnaround: int | None = field(default=None, init=False)

    def __post_init__(self):
        self.reset()

    def reset(self):
        """Restore the process to its initial state for a new simulation."""
        self.state = "New"
        self.remaining = self.duration
        self.start = self.finish = self.wait = self.turnaround = None

    def admit(self):
        self.state = "Ready"

    def dispatch(self, time):
        self.state = "Running"
        self.start = time

    def execute_tick(self):
        self.remaining -= 1

    def complete(self, time):
        self.state = "Terminated"
        self.finish = time
        self.wait = self.start - self.arrival
        self.turnaround = self.finish - self.arrival

