"""Continuously show the Pi camera feed until stopped.

This is the rough equivalent of running rpicam-hello in an endless preview
loop, but implemented in Python so it fits the rest of the project.
"""

import cv2
import signal
import sys

from src.camera import Camera


stop_requested = False


def _request_stop(signum, frame):
    del signum, frame
    global stop_requested
    stop_requested = True


def main():
    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)

    cam = Camera(warmup_seconds=2)
    picam = cam.start()

    print("Showing camera preview. Press q in the window or Ctrl+C to quit.")

    try:
        while True:
            if stop_requested:
                break

            frame = picam.capture_array()
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imshow("Pi Camera Preview", frame_bgr)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        try:
            cam.stop()
        except Exception:
            pass
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()