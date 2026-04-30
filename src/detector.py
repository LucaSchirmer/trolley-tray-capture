"""Aruco detector wrapper providing a small, testable API."""
import cv2
from typing import Tuple, Optional


class ArucoDetectorWrapper:
    def __init__(self, dict_type: int, params: Optional[cv2.aruco.DetectorParameters] = None):
        aruco_dict = cv2.aruco.getPredefinedDictionary(dict_type)
        if params is None:
            params = cv2.aruco.DetectorParameters()
        self._detector = cv2.aruco.ArucoDetector(aruco_dict, params)

    def detect(self, gray_image) -> Tuple[list, Optional[list], list]:
        corners, ids, rejected = self._detector.detectMarkers(gray_image)
        return corners, ids, rejected
