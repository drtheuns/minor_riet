from .webcam import predict_from_webcam, record
from .frames import FrameHandler, ImageHandler, predict_from_video

__all__ = [predict_from_webcam, record, FrameHandler,
           ImageHandler, predict_from_video]
