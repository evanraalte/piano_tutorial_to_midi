from dataclasses import dataclass, field
import cv2

import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore

from Contour import Contour
from VideoAnalyzer import VideoAnalyzer
from LabelWithRubberband import LabelWithRubberband

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class VideoPlayer(QtWidgets.QWidget):
    """consists of a video frame and a frame slider, along with logic to analyze the frame"""

    IMAGE_WIDTH = 1280
    IMAGE_HEIGHT = 720

    def __init__(self):
        super(VideoPlayer, self).__init__()
        layout = QtWidgets.QVBoxLayout()
        self.video_analyzer = VideoAnalyzer(width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT)
        self.video_analyzer.signal_contours_detected.connect(self.draw_contour_overlay)

        self.image_label = LabelWithRubberband()
        self.image_label.signal_selection_complete.connect(self.video_analyzer.detect_contours)
        self.image_label.setFixedHeight(self.IMAGE_HEIGHT)
        self.image_label.setFixedWidth(self.IMAGE_WIDTH)
        layout.addWidget(self.image_label)

        self.frame_slider = QtWidgets.QSlider(orientation=QtCore.Qt.Horizontal)
        self.frame_slider.setFixedWidth(self.IMAGE_WIDTH)
        self.frame_slider.setEnabled(False)
        self.frame_slider.valueChanged.connect(self.change_and_draw_frame)
        layout.addWidget(self.frame_slider)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def load_video(self, path: str):
        self.frame_slider.setEnabled(False)
        # self.start_note_slider.setEnabled(False)
        self.cap = cv2.VideoCapture(str(path))
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(self.cap.get(7))
        self.frame_slider.setValue(0)
        self.frame_slider.setEnabled(True)
        # self.start_note_slider.setEnabled(True)
        self.change_and_draw_frame(self.frame_slider.value())

    @classmethod
    def convert_cv_qt(cls, cv_img) -> QtGui.QPixmap:
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(cls.IMAGE_WIDTH, cls.IMAGE_HEIGHT, QtCore.Qt.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)

    def change_and_draw_frame(self, frame_num):
        logger.info(frame_num)
        self.cap.set(1, frame_num)
        _, cv_frame = self.cap.read()
        self.video_analyzer.set_frame(cv_frame)
        self.frame = self.convert_cv_qt(cv_frame)
        self.image_label.setPixmap(self.frame)
        # if key overlay was generated before, draw it again
        if self.video_analyzer.keys is not None:
            self.draw_contour_overlay(self.video_analyzer.keys)

    def draw_contour_overlay(self, contours: list[Contour]):
        frame_with_overlay = QtGui.QPixmap(self.frame)
        with QtGui.QPainter(frame_with_overlay) as painter:
            painter.setPen("Black")
            brush = QtGui.QBrush()
            brush.setStyle(QtCore.Qt.SolidPattern)
            for contour in contours:
                path = QtGui.QPainterPath()
                points = contour.as_qpoints(
                    image=self.image_label,
                    cap_width=self.video_analyzer.frame_width,
                    cap_height=self.video_analyzer.frame_height,
                )
                path.addPolygon(points)
                brush.setColor(contour.color)
                painter.fillPath(path, brush)
                painter.drawPolygon(points)
        self.image_label.setPixmap(frame_with_overlay)
