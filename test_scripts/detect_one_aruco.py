from picamera2 import Picamera2
import cv2
import time
import os
import numpy as np

DICT_TYPE = cv2.aruco.DICT_6X6_1000
TARGET_ID = 0
SAVE_PATH = "single_marker_shot.jpg"
EXPECTED_PATH = "expected_target_aruco.png"

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

marker_preview = np.zeros((400, 400), dtype=np.uint8)
cv2.aruco.generateImageMarker(aruco_dict, TARGET_ID, 400, marker_preview, 1)
cv2.imwrite(EXPECTED_PATH, marker_preview)

print(f"Expected marker saved as: {EXPECTED_PATH}")
os.system(f"timg {EXPECTED_PATH}")

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()
time.sleep(2)

captured = False

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    corners, ids, rejected = detector.detectMarkers(gray)

    if frame is not None and frame.size > 0:
        if ids is not None:
            detected_ids = ids.flatten().tolist()
            print(f"Detected IDs: {detected_ids}")

            if TARGET_ID in detected_ids and not captured:
                cv2.imwrite(SAVE_PATH, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                print(f"Saved {SAVE_PATH}")
                captured = True
        else:
            print("No marker detected")
    else:
        print("Warning: Received empty frame from camera")

    if cv2.waitKey(1) & 0xFF == ord('q') or captured:
        break

picam2.stop()
cv2.destroyAllWindows()
