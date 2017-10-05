"""
Make sure the webcam works with dlib
"""
import cv2
import dlib

video_capture = cv2.CaptureFromFile('../data/vid.avi')
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("../models/shape_predictor_68_face_landmarks.dat")

while True:
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    clahe_image = clahe.apply(gray)

    detections = detector(clahe_image, 1)

    for k, d in enumerate(detections):
        shape = predictor(clahe_image, d)
        for i in range(1, 68):
            # for each point, draw a red circle
            cv2.circle(frame, (shape.part(i).x, shape.part(i).y), 1, (0, 0, 255), thickness=2)

    cv2.imshow("image", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

