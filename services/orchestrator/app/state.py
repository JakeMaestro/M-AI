import time

class WSState:
    def __init__(self) -> None:
        self.connected: bool | None = None
        self.last_event_ts: float | None = None
        self.restarts: int = 0

    def mark_connected(self, value: bool) -> None:
        self.connected = value

    def mark_event(self) -> None:
        self.last_event_ts = time.time()

ws = WSState()
