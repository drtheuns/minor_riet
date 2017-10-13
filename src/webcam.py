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

    return predict


def predict_from_webcam():
    predict = get_predictor()
    for x in get_webcam_video():
        frame = FrameHandler(x) 
        frame.draw_points()

        predictions = [predict([np.array(x)]) for x in frame.get_vectorized_landmarks()]
        print(predictions)

        cv2.imshow('image', frame.frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    predict_from_webcam()

