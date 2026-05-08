"""Camera wrapper utilities for Picamera2 usage."""
from picamera2 import Picamera2
import time


class Camera:
    def __init__(self, warmup_seconds: float = 2.0):
        self._warmup = float(warmup_seconds)
        self._picam2 = None

    def start(self, resolution: tuple = None, mode: str = "preview"):
        """Start the camera.

        resolution: optional (width, height) tuple to request a specific capture size.
        mode: 'preview' or 'still'. 'still' will try to use a higher-quality still configuration.
        The method tries a few common Picamera2 configuration signatures and falls back
        to a preview configuration if necessary.
        """
        self._picam2 = Picamera2()
        config = None
        # Try to prefer still (high-res) captures when requested
        if mode == "still" or resolution is not None:
            # Try a couple of possible create_still_configuration signatures
            try:
                if resolution is not None:
                    config = self._picam2.create_still_configuration({"size": resolution})
                else:
                    config = self._picam2.create_still_configuration()
            except Exception:
                try:
                    if resolution is not None:
                        config = self._picam2.create_still_configuration(main={"size": resolution})
                    else:
                        config = self._picam2.create_still_configuration()
                except Exception:
                    config = None

        if config is None:
            # Fallback to preview configuration (optionally with size)
            try:
                if resolution is not None:
                    config = self._picam2.create_preview_configuration({"size": resolution})
                else:
                    config = self._picam2.create_preview_configuration()
            except Exception:
                config = self._picam2.create_preview_configuration()

        self._picam2.configure(config)
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
