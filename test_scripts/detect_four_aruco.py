"""Capture a frame once four required ArUco markers are visible.

The script streams frames from Picamera2, detects ArUco markers, and saves
an image when IDs 0, 1, 2, and 3 are all present in the same frame.
"""

from picamera2 import Picamera2
import cv2
import time
import signal
import sys
import select

DICT_TYPE = cv2.aruco.DICT_6X6_250
REQUIRED_IDS = {0, 1, 2, 3}
SAVE_PATH = "all_markers_shot.jpg"

stop_requested = False


def _request_stop(signum, frame):
    del signum, frame
    global stop_requested
    stop_requested = True


def _terminal_requested_quit() -> bool:
    """Return True if user typed q + Enter in terminal (SSH-friendly)."""
    if not sys.stdin.isatty():
        return False
    ready, _, _ = select.select([sys.stdin], [], [], 0)
    if ready:
        text = sys.stdin.readline().strip().lower()
        return text == "q"
    return False

def main():
    # Allow graceful shutdown via Ctrl+C or SIGTERM.
    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)

    # Create detector for the selected marker dictionary.
    aruco_dict = cv2.aruco.getPredefinedDictionary(DICT_TYPE)
    params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, params)

    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration())
    picam2.start()
    time.sleep(2)
    print("Press q then Enter in terminal to quit.")

    captured = False

    try:
        while True:
            # SSH-friendly termination path from terminal input/signals.
            if stop_requested or _terminal_requested_quit():
                print("Stop requested. Exiting...")
                break

            frame = picam2.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            corners, ids, rejected = detector.detectMarkers(gray)

            if ids is not None:
                detected_ids = set(ids.flatten().tolist())
                # Trigger only when all required marker IDs are simultaneously visible.
                if REQUIRED_IDS.issubset(detected_ids) and not captured:
                    cv2.imwrite(SAVE_PATH, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                    print(f"Saved {SAVE_PATH}")
                    captured = True

            # Visual overlay helps debug missed detections.
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            cv2.imshow("Four Marker Trigger", frame)

            if cv2.waitKey(1) & 0xFF == ord('q') or captured:
                break
    finally:
        picam2.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()