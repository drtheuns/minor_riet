"""
Maybe add all frames from the webcam in a buffer (queue) and
read them all one by one.
"""
import pickle
import os
import sys

import cv2
import numpy as np

from .frames import FrameHandler


def record(filename, seconds, **kwargs):
    """Records a video and saves it to a file

    Args:
        filename: the filepath to save the video to
        seconds: The amount of seconds to record.
    Kwargs:
        fourcc: The video codec to use. An exhaustive list is available on
            http://www.fourcc.org/codecs.php. Note that some might be
            platform dependant. Defaults to XVID
        frame_size: The width and height of the video. Defaults to (640, 480)
        fps: The amount of frames per second. Defaults to 10.0

    Returns:
        frame_count (int): The amount of frames that were recorded.
    """
    fourcc = kwargs.get('fourcc', ('X', 'V', 'I', 'D'))
    frame_size = kwargs.get('size', (640, 480))
    fps = kwargs.get('fps', 10)
    codec = cv2.cv.CV_FOURCC(*fourcc)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, frame_size[0])
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, frame_size[1])
    cap.set(cv2.cv.CV_CAP_PROP_FPS, fps)
    cap.set(cv2.cv.CV_CAP_PROP_FOURCC, codec)
    out = cv2.VideoWriter(filename, codec, fps, frame_size)

    total_frames = int(fps * seconds)
    frame_count = 0
    while (cap.isOpened() and frame_count < total_frames):
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            frame_count += 1
        else:
            break

    return frame_count


def record_to_file(session, video):
    project_root = os.path.dirname(sys.modules['__main__'].__file__)


def get_webcam_video(width, height):
    vc = cv2.VideoCapture(0)
    vc.set(3, width)
    vc.set(4, height)
    print(vc.isOpened())

    while True:
        ret, frame = vc.read()

        if not ret:
            return

        yield frame


def predict_from_webcam(args):
    emotions = ['anger', 'contempt', 'disgust', 'fear',
                'happy', 'neutral', 'sadness', 'surprise']

    with open('models/trained_svm_model', 'rb') as f:
        model = pickle.load(f)

    width, height = args.dimensions
    for frame in get_webcam_video(width, height):
        handler = FrameHandler(frame)

        if args.landmarks:
            handler.draw_landmarks()

        faces = np.array([handler.get_vectorized_landmarks()])
        if faces[0] is not None:
            prediction = model.predict(faces)
            if len(prediction) > 0:
                text = emotions[prediction[0]]
                cv2.putText(handler.frame, text, (40, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                            thickness=2)

        cv2.imshow('image', handler.frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
