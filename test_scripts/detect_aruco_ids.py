"""Print ArUco marker IDs whenever they are detected.

This script is meant for quickly checking printed markers and confirming that
OpenCV can see them with the expected dictionary. It reads the same JSON config
used by the configured capture script, then continuously prints detected IDs
frame by frame.
"""

from datetime import datetime
import argparse
import json
import os
import select
import signal
import sys
import time

import cv2
from picamera2 import Picamera2

DEFAULT_CONFIG_PATH = "configs/aruco_detection_config.json"
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


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Continuously print detected ArUco IDs for the configured dictionary."
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        help="Path to the JSON config file.",
    )
    return parser.parse_args()


def _load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)

    required_fields = ["aruco_dictionary", "camera_warmup_seconds", "window_name"]
    missing = [field for field in required_fields if field not in config]
    if missing:
        raise ValueError(f"Missing config fields: {', '.join(missing)}")

    return config


def _resolve_dictionary(dictionary_name: str):
    if not hasattr(cv2.aruco, dictionary_name):
        raise ValueError(
            f"Unknown ArUco dictionary '{dictionary_name}'. Use a valid cv2.aruco.DICT_* name."
        )
    return getattr(cv2.aruco, dictionary_name)


def _to_gray(frame):
    if frame.ndim == 2:
        return frame
    if frame.shape[2] == 4:
        return cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)
    return cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)


def _to_display_frame(frame):
    if frame.ndim == 2:
        return cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
    if frame.shape[2] == 4:
        return cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
    return frame


def main():
    args = _parse_args()
    config = _load_config(args.config)

    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)

    dict_type = _resolve_dictionary(config["aruco_dictionary"])
    aruco_dict = cv2.aruco.getPredefinedDictionary(dict_type)
    detector = cv2.aruco.ArucoDetector(aruco_dict, cv2.aruco.DetectorParameters())

    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration())
    picam2.start()
    time.sleep(float(config["camera_warmup_seconds"]))

    print(f"Loaded config: {args.config}")
    print(f"Dictionary: {config['aruco_dictionary']}")
    print("Press q then Enter in terminal to quit.")

    try:
        while True:
            if stop_requested or _terminal_requested_quit():
                print("Stop requested. Exiting...")
                break

            frame = picam2.capture_array()
            gray = _to_gray(frame)
            display_frame = _to_display_frame(frame)

            corners, ids, rejected = detector.detectMarkers(gray)
            del rejected

            if ids is not None:
                detected_ids = ids.flatten().tolist()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Detected IDs: {detected_ids}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No marker detected")

            cv2.aruco.drawDetectedMarkers(display_frame, corners, ids)
            cv2.imshow(str(config["window_name"]), display_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        try:
            picam2.stop()
        except Exception:
            pass
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
