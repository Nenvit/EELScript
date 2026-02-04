from threading import Thread, current_thread
import time


class Interval:
    def __init__(self, func=lambda: None, tick=1000, repeat=None):
        self.func = func
        self.tick = tick / 1000  # convert ms → seconds
        self.repeat = repeat
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        count = 0

        while self._running:
            time.sleep(self.tick)
            self.func()
            count += 1

            # Stop if repeat limit reached
            if self.repeat is not None and count >= self.repeat:
                break

        # Auto-cleanup
        self._running = False
        self._thread = None

    def stop(self):
        """External stop — still auto-cleans."""
        self._running = False

        # Only join if called from outside the timer thread
        if self._thread is not None and current_thread() != self._thread:
            self._thread.join()

        # Cleanup
        self._thread = None


class timeOut:
    def __init__(self, func=lambda: None, tick=1000):
        self.func = func
        self.tick = tick / 1000
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        time.sleep(self.tick)

        if self._running:
            self.func()

        # Auto-cleanup
        self._running = False
        self._thread = None

    def clear(self):
        """Cancel the timeout before it fires."""
        self._running = False

        # Only join if called from outside the timer thread
        if self._thread is not None and current_thread() != self._thread:
            self._thread.join()

        # Cleanup
        self._thread = None