import cv2

import frames


def test_webcam_faces_get_resized():
    """Test that the FrameHandler class is able to resize all faces in a frame.

    For now this is done graphically (the result is shown on screen, but the programmer)
    has to check the result himself. This should be changed to something automatic.
    The requirements are:
        - Correct amount of faces recognized
        - Each resized image has the right size (350x350 at the moment)
        - In an image with no faces, it should return an empty list
    """
    frame = frames.ImageHandler('../data/test/webcam_face.jpg')

    while True:
        cv2.imshow('image', frame.faces[0])
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    test_webcam_faces_get_resized()
