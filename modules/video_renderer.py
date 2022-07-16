import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore

import logging
import numpy as np

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class VideoRenderer(QtCore.QObject):
    finished = QtCore.Signal(np.ndarray)

    def __init__(self):
        super(VideoRenderer, self).__init__()
        self.frame_num = 0
        self.rendered_frame = None
        self.cap = None

    def set_frame(self, frame_num):
        self.frame_num = frame_num

    def render(self):
        frame = self.frame_num  # Could be updated while rendering
        self.cap.set(1, frame)
        _, cv_frame = self.cap.read()
        self.finished.emit(cv_frame)
        self.rendered_frame = frame

    def run(self):
        if self.cap is None:
            logger.error("Thread started without a valid capture")
            return

        while self.rendered_frame != self.frame_num:
            self.render()
