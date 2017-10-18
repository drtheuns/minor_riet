import unittest

import cv2


class TestWebcam(unittest.TestCase):

    def test_webcam_available(self):
        vc = cv2.VideoCapture(0)
        ret, frame = vc.read()
        self.assertTrue(ret, 'no video available')
