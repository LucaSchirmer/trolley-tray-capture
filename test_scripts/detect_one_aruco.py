"""Capture a frame when one target ArUco marker is detected.

The script generates a reference marker image, starts Picamera2 streaming,
detects markers per frame, and saves a shot when TARGET_ID is found.
It can be stopped via marker capture, OpenCV window keypress, or SSH terminal
input (q + Enter / Ctrl+C).
"""

from picamera2 import Picamera2
import argparse
import cv2
import time
import os
import signal
import sys
import select
import numpy as np
from datetime import datetime

DICT_TYPE = cv2.aruco.DICT_6X6_1000
TARGET_ID = 0
DEFAULT_FILE_BASENAME = "single_marker_shot"
EXPECTED_FILE_BASENAME = "expected_target_aruco"

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
        description="Capture an image when one target ArUco marker is detected."
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory where captured images are saved.",
    )
    parser.add_argument(
        "--name",
        default=DEFAULT_FILE_BASENAME,
        help="Base filename for captured images (timestamp is appended).",
    )
    parser.add_argument(
        "--show-expected",
        action="store_true",
        help="Generate and display the expected target ArUco marker image.",
    )
    return parser.parse_args()


def _build_capture_path(output_dir: str, base_name: str, extension: str = "jpg") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{timestamp}.{extension}"
    return os.path.join(output_dir, filename)

def main():
    args = _parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    # Allow graceful shutdown via Ctrl+C or SIGTERM.
    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)

    # Configure an ArUco detector tuned for robust marker detection.
    aruco_dict = cv2.aruco.getPredefinedDictionary(DICT_TYPE)
    params = cv2.aruco.DetectorParameters()

    params.adaptiveThreshWinSizeMin = 3
    params.adaptiveThreshWinSizeMax = 53
    params.adaptiveThreshWinSizeStep = 10
    params.minMarkerPerimeterRate = 0.02
    params.maxMarkerPerimeterRate = 4.0
    params.polygonalApproxAccuracyRate = 0.08
    params.maxErroneousBitsInBorderRate = 0.6
    params.errorCorrectionRate = 0.8

    detector = cv2.aruco.ArucoDetector(aruco_dict, params)

    if args.show_expected:
        # Save expected marker image so the user knows what to present.
        marker_preview = np.zeros((400, 400), dtype=np.uint8)
        cv2.aruco.generateImageMarker(aruco_dict, TARGET_ID, 400, marker_preview, 1)
        expected_path = _build_capture_path(args.output_dir, EXPECTED_FILE_BASENAME, "png")
        cv2.imwrite(expected_path, marker_preview)

        print(f"Expected marker saved as: {expected_path}")
        os.system(f"timg {expected_path}")

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

            if frame is not None and frame.size > 0:
                if ids is not None:
                    detected_ids = ids.flatten().tolist()
                    print(f"Detected IDs: {detected_ids}")

                    # Persist first frame containing the target marker ID.
                    if TARGET_ID in detected_ids and not captured:
                        save_path = _build_capture_path(args.output_dir, args.name)
                        cv2.imwrite(save_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                        print(f"Saved {save_path}")
                        captured = True
                else:
                    print("No marker detected")
            else:
                print("Warning: Received empty frame from camera")

            if cv2.waitKey(1) & 0xFF == ord('q') or captured:
                break
    finally:
        picam2.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
