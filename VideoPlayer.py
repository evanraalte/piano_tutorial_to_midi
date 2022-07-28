from dataclasses import dataclass, field
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)
import PySide6 as PySide6
from PySide6.QtCore import Qt, QRect, QSize, QPoint, Signal, QObject
from PySide6.QtGui import QImage, QPixmap, QPainter, QPainterPath, QBrush, QColor, QFontMetrics, QPalette
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSlider,
    QPushButton,
    QRubberBand,
    QHBoxLayout,
    QGridLayout,
    QComboBox,
)
from cv2 import COLOR_BGR2GRAY
from Color import Color
import cv2
import random
import numpy as np
from itertools import cycle, islice
from enum import Enum
import collections
from functools import partial
from Noterator import Notes, Note, Noterator

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# notes = cycle(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])


def find_start_note(notes) -> Notes:
    if len(notes) < len(Notes):
        raise Exception(f"Need at least {len(Notes)} notes to determine the start note")
    c_note = [n for n in "WBWBWWBWBWBW"]
    reference = collections.deque(c_note)
    for count in range(0, len(Notes)):
        if notes[0 : len(c_note)] == list(reference):
            return Notes(count)
        reference.rotate(-1)
    raise Exception("Start note not found")


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


@dataclass
class Contour:
    SATURATION_MAX = 255
    contour: np.array

    color: QColor = field(init=False, default=QColor.fromHsl(29, 255, 127))

    def __post_init__(self):
        pass

    def as_qpoints(self, image: QLabel, cap_width: int, cap_height: int):
        sfw = cap_width / image.width()
        sfh = cap_height / image.height()
        return [QPoint(c[0, 0] // sfw, c[0, 1] // sfh) for c in self.contour]


class LabelWithRubberband(QLabel):
    signal_selection_complete = Signal(QPoint, QPoint)

    def __init__(self):
        super(LabelWithRubberband, self).__init__()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)

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
        self.signal_selection_complete.emit(self.end_point, self.origin)
        self.rubberBand.hide()


class VideoAnalyzer(QObject):
    signal_contours_detected = Signal(dict)
    signal_start_note_updated = Signal(Notes)

    def __init__(self, width, height):
        super(VideoAnalyzer, self).__init__()
        self.keys = None
        self.qt_width = width
        self.qt_height = height

    @property
    def qt_scale_factor_width(self):
        return self.frame_width / self.qt_width

    @property
    def qt_scale_factor_height(self):
        return self.frame_height / self.qt_height

    def get_frame(self):
        return self.frame

    def set_frame(self, frame):
        self.frame = frame

    @property
    def frame_width(self):
        return len(self.frame[0])

    @property
    def frame_height(self):
        return len(self.frame)

    def detect_contours(self, origin: QPoint, end_point: QPoint):
        if self.frame is None:
            logger.error("Can't analyze frame because it doesn't exist")
            return

        # Determine the real coordinates of the selection frame
        x_start = int(min(origin.x(), end_point.x()) * self.qt_scale_factor_width)
        x_end = int(max(origin.x(), end_point.x()) * self.qt_scale_factor_width)
        y_start = int(min(origin.y(), end_point.y()) * self.qt_scale_factor_height)
        y_end = int(max(origin.y(), end_point.y()) * self.qt_scale_factor_height)
        logger.info(f"{x_start=} {x_end=} {y_start=} {y_end=}")

        # Crop our region of interest
        frame_cropped = self.frame[y_start:y_end, x_start:x_end]
        # Convert to greyscale
        frame_grey = cv2.cvtColor(frame_cropped, COLOR_BGR2GRAY)
        # Work with thresholds to BW from here (slider?)
        ret, frame_tresh = cv2.threshold(frame_grey, 180, 255, 0)
        # Find white contours (the white keys)
        contours_white, hierarchy = cv2.findContours(
            frame_tresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, offset=(x_start, y_start)
        )
        # Filter artifacts
        mask_white_keys = get_median_filtered_mask([cv2.contourArea(c) for c in contours_white])
        contours_white_valid = [("W", contour) for contour, valid in zip(contours_white, mask_white_keys) if valid]

        # Find white contours on inverted frame (ie black keys)
        contours_black, hierarchy = cv2.findContours(
            cv2.bitwise_not(frame_tresh), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, offset=(x_start, y_start)
        )
        # Filter artifacts
        mask_black_keys = get_median_filtered_mask([cv2.contourArea(c) for c in contours_black])
        contours_black_valid = [("B", contour) for contour, valid in zip(contours_black, mask_black_keys) if valid]
        # Sort contours (ie keys) from left to right
        contours = np.array(
            sorted(
                [x for x in contours_white_valid + contours_black_valid],
                key=lambda x: cv2.boundingRect(x[1][0]),
            ),
            dtype=object,
        )
        logger.info(f"number of contours: {len(contours)}")
        try:
            # The first entry of a contour is either 'W' or 'B'
            self.start_note = find_start_note([c[0] for c in contours])
            logger.info(f"Start note: {self.start_note}")
        except Exception:
            logger.info(f"Couldn't find start note, define it yourself")
            self.start_note = Notes.C
        self.signal_start_note_updated.emit(self.start_note)
        # The second entry of a contour are the points that cover its area
        self.signal_contours_detected.emit([Contour(contour=c[1]) for c in contours])


class VideoPlayer(QWidget):
    """consists of a video frame and a frame slider, along with logic to analyze the frame"""

    IMAGE_WIDTH = 1280
    IMAGE_HEIGHT = 720

    def __init__(self):
        super(VideoPlayer, self).__init__()
        layout = QVBoxLayout()
        self.video_analyzer = VideoAnalyzer(width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT)
        self.video_analyzer.signal_contours_detected.connect(self.draw_contour_overlay)

        self.image_label = LabelWithRubberband()
        self.image_label.signal_selection_complete.connect(self.video_analyzer.detect_contours)
        self.image_label.setFixedHeight(self.IMAGE_HEIGHT)
        self.image_label.setFixedWidth(self.IMAGE_WIDTH)
        layout.addWidget(self.image_label)

        self.frame_slider = QSlider(orientation=Qt.Horizontal)
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
    def convert_cv_qt(cls, cv_img) -> QPixmap:
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(cls.IMAGE_WIDTH, cls.IMAGE_HEIGHT, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

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
        frame_with_overlay = QPixmap(self.frame)
        with QPainter(frame_with_overlay) as painter:
            painter.setPen("Black")
            brush = QBrush()
            brush.setStyle(Qt.SolidPattern)
            for contour in contours:
                path = QPainterPath()
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


class StartNoteSelector(QWidget):
    signal_start_note_updated = Signal(Notes)

    def __init__(self):
        super(StartNoteSelector, self).__init__()
        layout = QGridLayout()
        self.buttons = {note: QPushButton(note.name, self) for note in Notes}
        for note, button in self.buttons.items():
            button.setFixedWidth(20)
            button.setAutoFillBackground(True)
            button.clicked.connect(partial(self.clicked, note))
            layout.addWidget(button, 1, note.value, 1, 1)
        self.dummy = Color("Blue")
        layout.addWidget(self.dummy, 2, 0, 1, len(self.buttons))
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def clicked(self, clicked_note):
        for note, button in self.buttons.items():
            pal = QPushButton().palette()
            if note == clicked_note:
                pal.setColor(QPalette.Button, "Green")
            button.setPalette(pal)
            button.update()
        self.signal_start_note_updated.emit(clicked_note)


class VideoEditPanel(QWidget):
    def __init__(self):
        super(VideoEditPanel, self).__init__()
        layout = QVBoxLayout()

        self.lbl_start_note = QLabel("Selected start note:")
        self.lbl_start_note.setFixedHeight(12)
        layout.addWidget(self.lbl_start_note)

        self.start_note_selector = StartNoteSelector()
        layout.addWidget(self.start_note_selector)

        self.lbl_midi_start_note = QLabel("Midi start note:")
        self.lbl_midi_start_note.setFixedHeight(12)
        layout.addWidget(self.lbl_midi_start_note)

        self.combo_box_midi_notes = QComboBox()
        layout.addWidget(self.combo_box_midi_notes)
        self.start_note_selector.signal_start_note_updated.connect(self.update_combo_box_midi_notes)
        layout.addWidget(self.start_note_selector)
        self.setLayout(layout)

    def update_combo_box_midi_notes(self, note):
        available_notes = [n for n in Noterator() if n.note == note]
        self.combo_box_midi_notes.clear()
        for n in available_notes:
            self.combo_box_midi_notes.addItem(str(n), n)
        pass


class BottomLayout(QWidget):
    def __init__(self):
        super(BottomLayout, self).__init__()
        layout = QHBoxLayout()

        self.video_player = VideoPlayer()
        layout.addWidget(self.video_player)

        self.video_edit_panel = VideoEditPanel()
        layout.addWidget(self.video_edit_panel)
        self.video_player.video_analyzer.signal_start_note_updated.connect(
            lambda x: self.video_edit_panel.start_note_selector.clicked(x)
        )

        # layout_col1 = QGridLayout()
        # layout_col1.addWidget(QLabel("start note:"), 0, 0, 1, 1)

        # self.start_note_slider = QSlider(orientation=Qt.Horizontal)
        # self.start_note_slider.setEnabled(False)
        # self.start_note_slider.setMinimum(0)
        # self.start_note_slider.setMaximum(11)
        # self.start_note_slider.setEnabled(False)
        # self.start_note_slider.valueChanged.connect(lambda x: self.start_note_label.setText(Note(x).name))
        # layout_col1.addWidget(self.start_note_slider, 0, 1, 1, 3)

        # self.start_note_label = QLabel(f"{Note(self.start_note_slider.value()).name}")
        # layout_col1.addWidget(self.start_note_label, 0, 4, 1, 1)

        # layout_col1.setContentsMargins(0, 0, 0, 0)
        # layout.addLayout(layout_col1)

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.video_player.load_video("Downloads/Speech Bubbles - The Smile [Piano Cover].mp4")
