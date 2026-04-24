import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Fehler: Kamera konnte nicht geöffnet werden.")
    raise SystemExit

ret, frame = cap.read()

if not ret:
    print("Fehler: Frame konnte nicht gelesen werden.")
else:
    print("Kamera funktioniert. Bildgröße:", frame.shape)
    cv2.imwrite("test_frame.jpg", frame)
    print("Testbild gespeichert als test_frame.jpg")

cap.release()
