from dataclasses import dataclass, field
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtCore import Qt, QRect, QSize, QPoint
from PySide6.QtGui import QImage, QPixmap, QPainter, QPainterPath, QBrush, QColor, QFontMetrics
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QPushButton, QRubberBand
from cv2 import COLOR_BGR2GRAY
from Color import Color
import cv2
import random
import numpy as np
from itertools import cycle, islice
from enum import Enum

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

notes = cycle(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])


def get_median_filtered_mask(signal, threshold=30):
    signal = np.array(signal)
    difference = np.abs(signal - np.median(signal))
    median_difference = np.median(difference)

    if median_difference == 0:
        s = 0
    else:
        s = difference / float(median_difference)

    ret = s < threshold
    return [ret] if type(ret) is bool else ret
    # mask = s < threshold
    # return signal[mask]


class Note(Enum):
    C = 0
    Db = 1
    D = 2
    Eb = 3
    E = 4
    F = 5
    Gb = 6
    G = 7
    Ab = 8
    A = 9
    Bb = 10
    B = 11


@dataclass
class Key:
    SATURATION_MAX = 255
    note: Note
    contour: np.array
    color: QColor = field(init=False)

    def __post_init__(self):
        hue = 29
        lightness = 0.5 * 255
        saturation = 1 * 255
        self.color = QColor.fromHsl(hue, saturation, lightness)


class QPiano(QPainter):
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
        self.frame_slider.valueChanged.connect(self.change_and_draw_frame)
        layout.addWidget(self.frame_slider)

        self.button_download = QPushButton(text="Detect keys", parent=self)
        self.button_download.clicked.connect(self.detect_keys)
        self.button_download.setEnabled(False)
        layout.addWidget(self.button_download)

        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)

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

    def detect_keys(self):

        # Determine scaling factors
        scale_factor_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) / self.IMAGE_WIDTH
        scale_factor_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / self.IMAGE_HEIGHT

        # Determine the real coordinates of the selection frame
        x_start = int(min(self.origin.x(), self.end_point.x()) * scale_factor_width)
        x_end = int(max(self.origin.x(), self.end_point.x()) * scale_factor_width)
        y_start = int(min(self.origin.y(), self.end_point.y()) * scale_factor_height)
        y_end = int(max(self.origin.y(), self.end_point.y()) * scale_factor_height)
        logger.info(f"{x_start=} {x_end=} {y_start=} {y_end=}")
        # Make a local copy of the cv_frame (perhaps unnessesary)
        frame = self.cv_frame[:][:]
        # cv2.imshow("frame", frame)
        # Crop our region of interest
        frame_cropped = frame[y_start:y_end, x_start:x_end]
        # cv2.imshow("frame_cropped", frame_cropped)
        # Convert to greyscale
        frame_grey = cv2.cvtColor(frame_cropped, COLOR_BGR2GRAY)
        # Work with tresholds to BW from here (slider?)
        ret, frame_tresh = cv2.threshold(frame_grey, 180, 255, 0)
        # Find white contours (the white keys)
        contours_white, hierarchy = cv2.findContours(
            frame_tresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, offset=(x_start, y_start)
        )
        mask_white_keys = get_median_filtered_mask([cv2.contourArea(c) for c in contours_white])
        contours_white_valid = [contour for contour, valid in zip(contours_white, mask_white_keys) if valid]

        # Find white contours on inverted frame (ie black keys)
        contours_black, hierarchy = cv2.findContours(
            cv2.bitwise_not(frame_tresh), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, offset=(x_start, y_start)
        )

        mask_black_keys = get_median_filtered_mask([cv2.contourArea(c) for c in contours_black])

        contours_black_valid = [contour for contour, valid in zip(contours_black, mask_black_keys) if valid]
        # Sort keys from left to right
        contours = np.array(
            sorted(
                [x for x in contours_white_valid + contours_black_valid],
                key=lambda x: cv2.boundingRect(x[0]),
            )
        )
        logger.info(f"number of keys: {len(contours)}")
        self.draw_key_overlay(contours, scale_factor_width, scale_factor_height)

        # Needs slider as well, we need to offset the keys (although we could detect it..)
        # list(islice(notes, 12 - 3))

        # Not so fan anymore of drawing in the cv_frame, rather draw in the application
        # for contour in contours:
        #     color = tuple(random.choices(range(100, 256), k=3))
        #     cv2.drawContours(frame, [contour], -1, color, thickness=cv2.FILLED)
        #     # x, y, w, h = cv2.boundingRect(contour)
        #     x, y = contour.mean(axis=0)[0]
        #     text = next(notes)
        #     fontFace = cv2.FONT_HERSHEY_SIMPLEX
        #     thickness = 1
        #     fontScale = 0.4

        #     area = cv2.contourArea(contour)
        #     tw, th = cv2.getTextSize(text, fontFace, fontScale, thickness)[0]
        #     cv2.putText(
        #         frame,
        #         text=text,
        #         org=(int(x) - tw // 2, int(y)),
        #         color=(0, 0, 0),
        #         fontFace=fontFace,
        #         fontScale=fontScale,
        #         thickness=thickness,
        #     )
        # self.image_label.setPixmap(self.convert_cv_qt(frame))

    def mousePressEvent(self, event):

        self.origin = event.pos()
        logger.info(self.origin)
        self.rubberBand.setGeometry(QRect(self.origin, QSize()))
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        self.end_point = event.pos()
        logger.info(event.pos())
        self.detect_keys()
        self.rubberBand.hide()

    def draw_key_overlay(self, contours, scale_factor_width, scale_factor_height):
        frame_with_overlay = QPixmap(self.frame)
        with QPainter(frame_with_overlay) as painter:
            painter.setPen("Black")
            brush = QBrush()
            brush.setStyle(Qt.SolidPattern)
            # Font placement is not super straightforward
            # font = painter.font()
            # font.setPixelSize(12)
            # painter.setFont(font)
            start_note = 0
            for idx, contour in enumerate(contours):
                note_num = (start_note + idx) % len(Note)
                path = QPainterPath()
                points = [QPoint(c[0, 0] // scale_factor_width, c[0, 1] // scale_factor_height) for c in contour]
                key = Key(note=Note(note_num), contour=contour)
                # x = min(points, key=lambda p: p.x()).x()
                # y = min(points, key=lambda p: p.y()).y() + QFontMetrics(font).height()
                # x, y = contour.mean(axis=0)[0]
                # x_scaled, y_scaled = int(x // scale_factor_width), int(y // scale_factor_height)
                # logger.info(f"{x=}, {y=}")
                path.addPolygon(points)
                brush.setColor(key.color)
                painter.fillPath(path, brush)
                painter.drawPolygon(points)
                # painter.drawText(x, y, key.note.name)
        self.image_label.setPixmap(frame_with_overlay)

    def change_and_draw_frame(self, frame_num):
        logger.info(frame_num)
        self.cap.set(1, frame_num)
        _, self.cv_frame = self.cap.read()
        self.frame = self.convert_cv_qt(self.cv_frame)
        self.image_label.setPixmap(self.frame)

    def load_video(self, path: str):
        self.cap = cv2.VideoCapture(str(path))
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(self.cap.get(7))
        self.frame_slider.setValue(0)
        self.frame_slider.setEnabled(True)
        self.change_and_draw_frame(self.frame_slider.value())
        self.button_download.setEnabled(True)
