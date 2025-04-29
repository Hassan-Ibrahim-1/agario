import time


class Timer:
    def __init__(self):
        self.reset()

    def reset(self):
        self._start = time.perf_counter()

    # in seconds
    def elapsed(self) -> float:
        return time.perf_counter() - self._start

    def elapsed_millis(self) -> float:
        return self.elapsed() * 1000.0
