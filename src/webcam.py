"""
Maybe add all frames from the webcam in a buffer (queue) and
read them all one by one.
"""
import pickle

import cv2
import dlib

from train_model import get_landmarks


class WebcamReader(object):

    def __init__(self, dat_file='../models/shape_predictor_68_face_landmarks.dat'):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(dat_file)
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        
        with open('../models/trained_svm_model', 'r') as f:
            self.model = pickle.load(f)

    def get_webcam_video(self):
        vc = cv2.VideoCapture(0)
        while True:
            ret, frame = vc.read()
            
            if not ret:
                return

            yield frame

    def get_facial_detections(self, frame):
        clahe_image = self.clahe.apply(frame)
        detections = self.detector(clahe_image, 1)
        return detections, clahe_image

    def to_grayscale(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def draw_points(self, frame, clahe_image, detections):
        for k, d in enumerate(detections):
            shape = self.predictor(clahe_image, d)
            for i in range(1, 68):
                cv2.circle(frame, (shape.part(i).x, shape.part(i).y), 1, (0, 0, 255), thickness=1)

    def play(self):
        for frame in self.get_webcam_video():
            gray = self.to_grayscale(frame)
            detections, clahe_image = self.get_facial_detections(gray)
            self.draw_points(frame, clahe_image, detections)
            cv2.imshow('image', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break;


if __name__ == '__main__':
    reader = WebcamReader()
    reader.play()


