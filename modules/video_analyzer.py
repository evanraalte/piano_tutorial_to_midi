import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore

from modules.note_tools import Notes, find_start_note
from modules.contour import Contour
from utils.filters import get_median_filtered_mask

import cv2
import numpy as np

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class VideoAnalyzer(QtCore.QObject):
    signal_contours_detected = QtCore.Signal(dict)
    signal_start_note_updated = QtCore.Signal(Notes)

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

    def detect_contours(self, origin: QtCore.QPoint, end_point: QtCore.QPoint):
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
        frame_grey = cv2.cvtColor(frame_cropped, cv2.COLOR_BGR2GRAY)
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

        # Contract the contours to omit the black spacing between the keys (maybe make a slider with advanced options)
        kernel = np.ones((3, 3), np.uint8)
        blank = np.zeros(self.frame.shape)
        cv2.drawContours(blank, contours_black, -1, (255, 255, 255), -1)
        erosion_image5 = cv2.erode(blank, kernel, iterations=1)

        # Iteration #2: Find white contours on the frame with contracted contours (no offset, because relative to frame)
        # https://stackoverflow.com/questions/68105013/how-to-draw-the-contour-inside-the-contour-opencv
        contours_black, hierarchy = cv2.findContours(
            np.uint8(erosion_image5[:, :, 0]), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
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
