from pathlib import Path
import cv2
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore

from modules.contour import Contour
from modules.video_analyzer import VideoAnalyzer
from modules.label_with_rubberband import LabelWithRubberband
from modules.video_renderer import VideoRenderer
from modules.frame_mode import FrameMode
import logging
import numpy as np

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class VideoPlayer(QtWidgets.QWidget):
    """consists of a video frame and a frame slider, along with logic to analyze the frame"""

    IMAGE_WIDTH = 1280
    IMAGE_HEIGHT = 720
    SLIDER_MULTIPLIER = 1

    signal_video_loaded = QtCore.Signal()
    signal_frame_selected = QtCore.Signal()

    def set_contours(self, contours):
        self.contours = contours

    def __init__(self):
        super(VideoPlayer, self).__init__()
        layout = QtWidgets.QVBoxLayout()
        self.video_analyzer = VideoAnalyzer(width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT)
        self.video_analyzer.signal_contours_detected.connect(self.draw_contour_overlay)
        self.video_analyzer.signal_contours_detected.connect(self.set_contours)

        self.image_label = LabelWithRubberband()
        self.image_label.signal_selection_complete.connect(self.video_analyzer.detect_contours)
        self.image_label.setFixedHeight(self.IMAGE_HEIGHT)
        self.image_label.setFixedWidth(self.IMAGE_WIDTH)
        self.image_label.signal_selection_complete.connect(lambda x, y: self.signal_frame_selected.emit())
        layout.addWidget(self.image_label)

        self.frame_slider = QtWidgets.QSlider(orientation=QtCore.Qt.Horizontal)
        self.frame_slider.setFixedWidth(self.IMAGE_WIDTH)
        self.frame_slider.setEnabled(False)
        self.frame_slider.valueChanged.connect(self.request_frame_from_capture)
        layout.addWidget(self.frame_slider)

        self.lbl_frame_mode = QtWidgets.QLabel(self.image_label.mode.name)
        self.image_label.signal_mode_updated.connect(lambda m: self.lbl_frame_mode.setText(m.name))
        layout.addWidget(self.lbl_frame_mode)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.thread = QtCore.QThread()
        self.worker = VideoRenderer()
        self.worker.finished.connect(self.draw_cv_image)
        self.worker.finished.connect(self.thread.quit)
        self.thread.started.connect(self.worker.run)
        self.worker.moveToThread(self.thread)

    def set_mode(self, mode: FrameMode):
        self.image_label.mode = mode

    def load_video(self, path: Path):
        self.frame_slider.setEnabled(False)
        # self.start_note_slider.setEnabled(False)
        self.video_path = path
        self.cap = cv2.VideoCapture(str(path))
        self.worker.cap = self.cap
        self.thread.start()
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(self.cap.get(7) / self.SLIDER_MULTIPLIER)
        self.frame_slider.setValue(0)
        self.frame_slider.setEnabled(True)
        # self.start_note_slider.setEnabled(True)
        self.request_frame_from_capture(self.frame_slider.value())
        self.signal_video_loaded.emit()

    @classmethod
    def convert_cv_qt(cls, cv_img) -> QtGui.QPixmap:
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(cls.IMAGE_WIDTH, cls.IMAGE_HEIGHT, QtCore.Qt.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)

    def draw_cv_image(self, cv_frame):
        # print("Drawing")
        try:
            self.video_analyzer.set_frame(cv_frame)
            self.frame = self.convert_cv_qt(cv_frame)
            self.image_label.setPixmap(self.frame)
        except cv2.error:
            logger.debug("Detected an empty frame, skipping")
            pass
    def request_frame_from_capture(self, slider_value):
        frame_num = slider_value * self.SLIDER_MULTIPLIER
        self.worker.set_frame(frame_num)

        # The thread is started again when it previously closed because it was idle and an update is needed
        if not self.thread.isRunning() and frame_num != self.worker.rendered_frame:
            self.thread.start()

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
