import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSlider,
)
from Color import Color
import cv2

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class VideoPlayer(QWidget):
    IMAGE_WIDTH = 852
    IMAGE_HEIGHT = 480

    def __init__(self):
        super(VideoPlayer, self).__init__()
        layout = QVBoxLayout()

        self.image = QImage()
        self.image_label = QLabel()
        self.image_label.setMinimumHeight(self.IMAGE_HEIGHT)
        self.image_label.setMinimumWidth(self.IMAGE_WIDTH)
        layout.addWidget(self.image_label)

        self.frame_slider = QSlider(orientation=Qt.Horizontal)
        self.frame_slider.setEnabled(False)
        self.frame_slider.valueChanged.connect(self.change_frame)
        layout.addWidget(self.frame_slider)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.IMAGE_WIDTH, self.IMAGE_HEIGHT, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def change_frame(self, frame_num):
        logger.info(frame_num)
        self.cap.set(1, frame_num)
        _, frame = self.cap.read()
        self.image_label.setPixmap(self.convert_cv_qt(frame))

    def load_video(self, path: str):
        path = "Downloads/Speech Bubbles - The Smile [Piano Cover].mp4"
        self.cap = cv2.VideoCapture(str(path))
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(self.cap.get(7))
        self.frame_slider.setValue(0)
        self.frame_slider.setEnabled(True)
        self.change_frame(self.frame_slider.value())
