from picamera2 import Picamera2
import cv2
import time

print("Kamera initialisieren...")
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()
time.sleep(2)

print("Foto machen...")
frame = picam2.capture_array()
cv2.imwrite("test_photo.jpg", frame)
print("✅ Foto gespeichert: test_photo.jpg")

picam2.stop()
print("Fertig!")
