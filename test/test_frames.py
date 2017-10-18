import unittest

from emotionreader import frames


class TestFrameHandler(unittest.TestCase):
    """Test that the FrameHandler class is able to resize all faces in a frame.

    For now this is done graphically (the result is shown on screen, but the programmer)
    has to check the result himself. This should be changed to something automatic.
    The requirements are:
        - Correct amount of faces recognized
        - Each resized image has the right size (350x350 at the moment)
        - In an image with no faces, it should return an empty list
    """

    def setUp(self):
        self.handler = frames.ImageHandler('data/test/webcam_face.jpg')

    def test_has_correct_amount(self):
        self.assertEqual(len(self.handler.faces), 1)
        
    def test_correct_resize(self):
        pass

