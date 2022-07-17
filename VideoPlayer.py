import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap, QPainter
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSlider,
)
from cv2 import COLOR_BGR2GRAY
from Color import Color
import cv2
import random
import numpy

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class QPiano(QPainter):
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    def set_attributes(self):
        self.num_keys = 88
        self.start_note = self.notes[0]
        self.x = 0
        self.w = 852
        self.y = 200
        self.h = 100

    def draw(self):
        self.setPen("Red")
        self.drawRect(self.x, self.y, self.w, self.h)

        # key_width = int(self.w / self.num_keys)
        # self.setPen("Green")
        # for x in range(self.x, self.x + self.w, key_width):
        #     self.drawRect(x, self.y, key_width, self.h)


class VideoPlayer(QWidget):
    IMAGE_WIDTH = 1280
    IMAGE_HEIGHT = 720

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
        self.load_video("Downloads/Speech Bubbles - The Smile [Piano Cover].mp4")

    def convert_cv_qt(self, cv_img) -> QPixmap:
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
        Y_OFFSET = 450
        frame_cropped = frame[:][Y_OFFSET : Y_OFFSET + 225]
        frame_grey = cv2.cvtColor(frame_cropped, COLOR_BGR2GRAY)
        ret, frame_tresh = cv2.threshold(frame_grey, 170, 255, 0)
        contours_white, hierarchy = cv2.findContours(
            frame_tresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, offset=(0, Y_OFFSET)
        )
        contours_black, hierarchy = cv2.findContours(
            cv2.bitwise_not(frame_tresh), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, offset=(0, Y_OFFSET)
        )
        for contour in contours_white + contours_black:
            color = tuple(random.choices(range(100, 256), k=3))
            cv2.drawContours(frame, [contour], -1, color, thickness=cv2.FILLED)

        pix = QPixmap(self.IMAGE_WIDTH, self.IMAGE_HEIGHT)
        with QPainter(pix) as painter:
            # https://stackoverflow.com/questions/13840289/how-to-use-qrubberband-with-qrect-class-in-pyqt
            painter.drawPixmap(0, 0, self.convert_cv_qt(frame))
            self.image_label.setPixmap(pix)

    def load_video(self, path: str):
        self.cap = cv2.VideoCapture(str(path))
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(self.cap.get(7))
        self.frame_slider.setValue(0)
        self.frame_slider.setEnabled(True)
        self.change_frame(self.frame_slider.value())
