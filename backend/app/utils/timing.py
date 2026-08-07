import time
from contextlib import contextmanager


class Timer:
    def __init__(self):
        self.spans: dict[str, float] = {}
        self.start_times: dict[str, float] = {}

    def start(self, name: str):
        self.start_times[name] = time.perf_counter()

    def stop(self, name: str):
        if name in self.start_times:
            elapsed = (time.perf_counter() - self.start_times[name]) * 1000
            self.spans[name] = elapsed
            return elapsed
        return 0.0

    @contextmanager
    def span(self, name: str):
        self.start(name)
        try:
            yield
        finally:
            self.stop(name)

    def total_ms(self) -> float:
        if "total" in self.spans:
            return self.spans["total"]
        return sum(self.spans.values())

    def cost_inr(self) -> float:
        return 0.0
