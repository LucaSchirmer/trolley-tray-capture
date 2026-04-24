from picamera2 import Picamera2
import cv2
import time

DICT_TYPE = cv2.aruco.DICT_6X6_250
REQUIRED_IDS = {0, 1, 2, 3}
SAVE_PATH = "all_markers_shot.jpg"

aruco_dict = cv2.aruco.getPredefinedDictionary(DICT_TYPE)
params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, params)

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()
time.sleep(2)

captured = False

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    corners, ids, rejected = detector.detectMarkers(gray)

    if ids is not None:
        detected_ids = set(ids.flatten().tolist())
        if REQUIRED_IDS.issubset(detected_ids) and not captured:
            cv2.imwrite(SAVE_PATH, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            print(f"Saved {SAVE_PATH}")
            captured = True

    cv2.aruco.drawDetectedMarkers(frame, corners, ids)
    cv2.imshow("Four Marker Trigger", frame)

    if cv2.waitKey(1) & 0xFF == ord('q') or captured:
        break

picam2.stop()
cv2.destroyAllWindows()