"""Minimal Picamera2 still-photo test.

This script initializes Picamera2, waits briefly for exposure to settle,
captures a single frame, and saves it as test_photo.jpg.
"""

from picamera2 import Picamera2
import cv2
import time

def main():
	print("Initializing camera...")
	picam2 = Picamera2()
	# Still configuration is suitable for one-shot captures.
	picam2.configure(picam2.create_still_configuration())
	picam2.start()
	time.sleep(2)

	print("Taking photo...")
	frame = picam2.capture_array()
	# Save captured frame for visual verification.
	cv2.imwrite("test_photo.jpg", frame)
	print("Photo saved: test_photo.jpg")

	picam2.stop()
	print("Done!")


if __name__ == "__main__":
	main()
