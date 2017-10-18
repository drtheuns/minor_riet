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

    Class attributes:
        predictor: The dlib facial landmarks shape predictor
        detector: The dlib face detector
        clahe: The cv2 CLAHE algorithm

    Attributes:
        frame: The frame this class operates on
        gray: The frame in grayscale
        clahe_image: The frame after the CLAHE algorithm has been used on it
        detections: The rectangles with coordinates of each face detected in the frame.
        sub_detections: Re-checked detections of each resized face frame.
    """

    predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
    detector = dlib.get_frontal_face_detector()
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    def __init__(self, frame):
        self.frame = frame
        gray = self._as_grayscale()
        self.clahe_image = self.clahe.apply(gray)
        self.detections = self.detector(self.clahe_image, 1)
        self.sub_detections = []

        if self.detections:
            self.faces = self._resize_to_face(gray)

            for face in self.faces:
                det_faces = self.detector(face, 1)
                # We know there is 1, and only 1, face in each item of
                # self.faces, but if this re-detection of the face fails and
                # we were to assume there is a face, the program crashes.
                if len(det_faces) == 1:
                    self.sub_detections.append(det_faces[0])

    def _as_grayscale(self):
        return cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

    def _rect_to_bb(self, rect):
        """Return a tuple with the x & y coordinates, and the width and height
        of a rectangle.

        Dlib's frontal face detector returns every face as a dlib.dlib.rectangle
        object. This is a helper method which can be used to get the face
        from an image.
        """
        x = rect.left()
        y = rect.top()
        w = rect.right() - x
        h = rect.bottom() - y
        return (x, y, w, h)

    def _resize_to_face(self, gray):
        """Creates 350x350 frames of each face in the image.
        
        The prediction model needs to have data of faces in the same
        dimensions as that it was trained in. For this reason, before
        we can create the facial landmarks, this method needs to be called
        to make sure we have valid images.

        Results are stored in self.faces
        """
        # make sure that if the method is called again, we don't get doubles.
        faces = []
        for face in self.detections:
            x, y, w, h = self._rect_to_bb(face)
            # cut the grayscales original frame to size
            cut = gray[y:y+h, x:x+w]
            resized = cv2.resize(cut, (350, 350))
            resized = self.clahe.apply(resized)
            faces.append(resized)
        return faces

    def draw_points(self, thickness=1):
        """Draw the facial landmarks on the original frame."""
        for d in self.detections:
           shape = self.predictor(self.clahe_image, d)
           for i in range(0, 68):
                cv2.circle(self.frame, (shape.part(i).x, shape.part(i).y),
                        1, (0, 0, 255), thickness=thickness)

    def get_shapes(self):
        """Get all the facial landmarks in the frame
        
        Each face in a frame can be detected (see `FrameHandler.detections`).
        This method will then return the 68 facial landmarks for each detected
        face in the frame.
        """
        return [self.predictor(self.clahe_image, d)
                for d in self.sub_detections
                if self.sub_detections]

    def get_vectorized_landmarks(self):
        result = []
        for shape in self.get_shapes():
            xlist = []
            ylist = []
            
            for i in range(0, 68):
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
       

class ImageHandler(FrameHandler):
    """Handles an image from a filepath.

    This is mostly useful for testing.
    """
    def __init__(self, filepath):
        frame = cv2.imread(filepath)
        super(ImageHandler, self).__init__(frame)
