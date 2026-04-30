"""Capture a frame when all configured ArUco markers are visible.

Configuration is loaded from a JSON file so dictionary and marker IDs can be
changed without editing Python code.
"""

import argparse
import cv2
import os
import select
import signal
import sys
from datetime import datetime

from src.camera import Camera
from src.config_loader import load_config, resolve_dictionary
from src.detector import ArucoDetectorWrapper

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
        description="Capture an image when configured ArUco markers are detected."
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        help="Path to JSON config file.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory where captured images are saved.",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Optional base filename override for captured images.",
    )
    return parser.parse_args()


def _build_capture_path(output_dir: str, base_name: str, extension: str = "jpg") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{timestamp}.{extension}"
    return os.path.join(output_dir, filename)


def main():
    args = _parse_args()
    config = load_config(args.config)
    os.makedirs(args.output_dir, exist_ok=True)

    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)

    dict_type = resolve_dictionary(config["aruco_dictionary"])
    required_ids = {int(marker_id) for marker_id in config["required_ids"]}
    base_name = args.name if args.name else str(config["default_output_basename"])

    detector_wrapper = ArucoDetectorWrapper(dict_type)

    cam = Camera(warmup_seconds=config["camera_warmup_seconds"])
    picam = cam.start()

    print(f"Loaded config: {args.config}")
    print(f"Dictionary: {config['aruco_dictionary']}")
    print(f"Required IDs: {sorted(required_ids)}")
    print("Press q then Enter in terminal to quit.")

    captured = False

    try:
        while True:
            if stop_requested or _terminal_requested_quit():
                print("Stop requested. Exiting...")
                break

            frame = picam.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            corners, ids, rejected = detector_wrapper.detect(gray)
            # rejected is unused in this flow

            if ids is not None:
                detected_ids = set(ids.flatten().tolist())
                if required_ids.issubset(detected_ids) and not captured:
                    save_path = _build_capture_path(args.output_dir, base_name)
                    cv2.imwrite(save_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                    print(f"Saved {save_path}")
                    captured = True

            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            cv2.imshow(str(config["window_name"]), frame)

            if cv2.waitKey(1) & 0xFF == ord("q") or captured:
                break
    finally:
        try:
            cam.stop()
        except Exception:
            pass
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
