"""
Maybe add all frames from the webcam in a buffer (queue) and
read them all one by one.
"""
import pickle

import cv2
import dlib
import numpy as np

from frames import FrameHandler


def get_webcam_video():
    vc = cv2.VideoCapture(0)
    while True:
        ret, frame = vc.read()

        if not ret:
            return

        yield frame


def get_predictor():
    with open('../models/trained_svm_model', 'r') as f:
        model = pickle.load(f)

    def predict(landmarks):
        return model.predict(landmarks)

    def predict_proba(landmarks):
        return model.predict_proba(landmarks)

    return predict, predict_proba


def predict_from_webcam():
    emotions = ['anger', 'contempt', 'disgust', 'fear',
            'happy', 'neutral', 'sadness', 'surprise']
    predict, predict_proba = get_predictor()
    for x in get_webcam_video():
        frame = FrameHandler(x) 
        # frame.draw_points()

        faces = np.array(frame.get_vectorized_landmarks())

        if faces.any():
            prediction = predict(faces)
            print(predict_proba(faces))
            for i, det in enumerate(frame.detections):
                x = det.left()
                y = det.top()
                cv2.putText(frame.frame, emotions[prediction[i]], (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness=2)
            # print(prediction)

        cv2.imshow('image', frame.frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    predict_from_webcam()

