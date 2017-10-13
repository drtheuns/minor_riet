"""
Common frame handling functionality
"""
import math

import cv2
import dlib
import numpy as np


class FrameHandler(object):
    """
    Handle common transformations for frames.
    """

    predictor = dlib.shape_predictor('../models/shape_predictor_68_face_landmarks.dat')
    detector = dlib.get_frontal_face_detector()
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    def __init__(self, frame):
        self.frame = frame
        self.clahe_image = self.clahe.apply(self._as_grayscale())

    def _as_grayscale(self):
        return cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

    def draw_points(self, thickness=1):
        """Draw the facial landmarks on the original frame."""
        for d in self.detections:
           shape = self.predictor(self.clahe_image, d)
           for i in range(1, 68):
                cv2.circle(self.frame, (shape.part(i).x, shape.part(i).y),
                        1, (0, 0, 255), thickness=thickness)

    def get_shapes(self):
        """Get all the facial landmarks in the frame
        
        Each face in a frame can be detected (see `FrameHandler.detections`).
        This method will then return the 68 facial landmarks for each detected
        face in the frame.
        """
        return [self.predictor(self.clahe_image, d) for d in self.detections]

    def get_vectorized_landmarks(self):
        result = []
        for shape in self.get_shapes():
            xlist = []
            ylist = []
            
            for i in range(1, 68):
                xlist.append(float(shape.part(i).x))
                ylist.append(float(shape.part(i).y))

            xmean = np.mean(xlist)
            ymean = np.mean(ylist)
            xcentral = [(x - xmean) for x in xlist]
            ycentral = [(y - ymean) for y in ylist]

            landmarks_vectorised = []
            for x, y, w, z in zip(xcentral, ycentral, xlist, ylist):
                landmarks_vectorised.append(w)
                landmarks_vectorised.append(z)
                meannp = np.asarray((ymean, xmean))
                coornp = np.asarray((z, w))
                dist = np.linalg.norm(coornp - meannp)
                landmarks_vectorised.append(dist)
                landmarks_vectorised.append(int(math.atan((y-ymean) / (x-xmean)) * 360/math.pi))
            
            result.append(landmarks_vectorised)
        return result

    @property
    def detections(self):
        return self.detector(self.clahe_image, 1)

        
class ImageHandler(FrameHandler):
    """
    Handles an image from a filepath
    """
    def __init__(self, filepath):
        frame = cv2.imread(filepath)
        super(ImageHandler, self).__init__(frame)
