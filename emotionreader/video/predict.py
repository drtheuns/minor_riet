"""
Handle the prediction of video frames
"""
import multiprocessing as mp
import pickle

import cv2
import numpy as np

from .frames import FrameHandler
from ..utils import average_emotions


class Worker(mp.Process):

    """
    A worker process that handles frames from an input queue, and passes
    the vectorized landmarks into an output queue.

    This process will keep going until the input queue receives a None value.
    """

    def __init__(self, input_queue, output_queue):
        """Initialize the worker.

        Args:
            input_queue (multiprocessing.JoinableQueue): The input queue
                of frames to handle. The frames are expected to be a tuple
                with (frame_index, frame). The index is necessary to preserve
                the frame ordering after processing is done.
            output_queue (multiprocessing.Queue): The output queue where the
                resulting landmarks are stored. The result is a tuple with
                (frame_index, vectorized_landmarks).
        """
        super(Worker, self).__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue

    def run(self):
        """Read frames from the input queue, get the vectorized landmarks
        from the frame, and move the result to the output queue.
        """
        for idx, frame in iter(self.input_queue.get, None):
            handler = FrameHandler(frame)
            face = np.array(handler.get_vectorized_landmarks())
            if face is None:
                self.output_queue.put((idx, []))
            else:
                self.output_queue.put((idx, face))
            self.input_queue.task_done()


def get_frames(path):
    vc = cv2.VideoCapture(path)
    count = 0
    while vc.isOpened():
        ret, frame = vc.read()
        if not ret:
            return
        count += 1
        yield count, frame


def predict_video(path, workers):
    with open('models/trained_svm_model', 'rb') as f:
        model = pickle.load(f)

    input_queue = mp.JoinableQueue()
    output_queue = mp.Queue()

    for i in range(workers):
        Worker(input_queue, output_queue).start()

    for idx, frame in get_frames(path):
        input_queue.put((idx, frame))

    input_queue.join()

    for i in range(workers):
        input_queue.put(None)

    queue_list = []
    while output_queue.qsize() != 0:
        queue_list.append(output_queue.get())

    # sort by the frame index
    s_items = sorted(queue_list, key=lambda x: x[0])
    landmarks = [x[1] for x in s_items]

    predictions = model.predict_proba(landmarks)
    return predictions


def predict_from_video(args):
    predict_video(args.path, args.workers)
