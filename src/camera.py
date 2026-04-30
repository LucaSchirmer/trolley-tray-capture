"""Camera wrapper utilities for Picamera2 usage."""
from picamera2 import Picamera2
import time


class Camera:
    def __init__(self, warmup_seconds: float = 2.0):
        self._warmup = float(warmup_seconds)
        self._picam2 = None

    def start(self):
        self._picam2 = Picamera2()
        self._picam2.configure(self._picam2.create_preview_configuration())
        self._picam2.start()
        time.sleep(self._warmup)
        return self._picam2

    def stop(self):
        if self._picam2 is not None:
            try:
                self._picam2.stop()
            except Exception:
                pass
            self._picam2 = None

    def capture_array(self):
        if self._picam2 is None:
            raise RuntimeError("Camera not started")
        return self._picam2.capture_array()
