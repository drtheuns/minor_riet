"""
Common frame handling functionality
"""
import math

import cv2
import dlib
import numpy as np


class FrameHandler(object):
    """Handle all necessary transformations of a frame to predict
    the facial expressions.

    To simplify the process and to achieve consistent results, this class
    only focusses on one single face. If there are multiple faces in the frame,
    only the first detected face will be returned.

    Detecting multiple faces would require we track where in subsequent frames
    a persons face is, and make sure the data is aligned with the faces.
    Our concept for this assignment doesn't involve multiple faces, so this
    functionality is forsaken in favour of a single face.

    Class attributes:
        predictor: The dlib facial landmarks shape predictor
        detector: The dlib face detector
        clahe: The cv2 CLAHE algorithm
    Attributes:
        detection: The detected face from the original frame
        resized_frame: A new frame, resized from the original frame
            based on the detected face.
        resized_detection: The detections of the face from the
            resized frame.
    """

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(
        'models/shape_predictor_68_face_landmarks.dat')

    def __init__(self, frame):
        self.frame = frame
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.clahe_image = self.clahe.apply(gray)

    def _resize_face(self, rect):
        """Resize the given face to 350x350 (same as dataset)

        Args:
            rect: The rectangle of the face. This is the area of the frame
                  that will be cut from the frame.
        Returns:
            frame | None: A resized version of the `self.clahe_image`,
                          or None is resizing failed.
        """
        x = rect.left()
        y = rect.top()
        w = rect.right() - x
        h = rect.bottom() - y
        cut = self.clahe_image[y:y+h, x:x+w]
        try:
            return cv2.resize(cut, (350, 350))
        except:
            return None

    def get_vectorized_landmarks(self, resized=True):
        """Get the vectorized landmarks of the frame.

        Args:
            resized (bool): If true, gets the landmarks from the resized
                            frames, otherwise, use the original frame.
        """
        if resized:
            frame = self.resized_frame
            rect = self.resized_detection
        else:
            frame = self.clahe_image
            rect = self.detection

        if rect is None:
            return None

        shape = self.predictor(frame, rect)
        xlist = []
        ylist = []
        for i in range(68):
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
            landmarks_vectorised.append((math.atan2(y, x)*360)/(2*math.pi))
        return landmarks_vectorised

    def draw_landmarks(self, thickness=1):
        # Can't draw that which doesn't exist.
        if self.detections is None:
            return
        shape = self.predictor(self.clahe_image, self.detection)
        for i in range(68):
            cv2.circle(self.frame, (shape.part(i).x, shape.part(i).y),
                       1, (0, 0, 255), thickness=thickness)

    @property
    def detection(self):
        if not hasattr(self, '_detections'):
            self._detections = self.detector(self.clahe_image, 1)
        return self._detections[0] if len(self._detections) > 0 else None

    @property
    def resized_frame(self):
        if not hasattr(self, '_resized'):
            if self.detection:
                self._resized = self._resize_face(self.detection)
            else:
                self._resized = None
        return self._resized

    @property
    def resized_detection(self):
        if not hasattr(self, '_re_detections'):
            if self.resized_frame is not None:
                self._re_detections = self.detector(self.resized_frame, 1)
            else:
                self._re_detections = []
        return self._re_detections[0] if len(self._re_detections) > 0 else None


class ImageHandler(FrameHandler):
    """Handles an image from a filepath.

    This is mostly useful for testing and training the model.
    """
    def __init__(self, filepath):
        frame = cv2.imread(filepath)
        super(ImageHandler, self).__init__(frame)
