from dataclasses import dataclass, field
import numpy as np

import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@dataclass
class Contour:
    SATURATION_MAX = 255
    contour: np.array

    color: QtGui.QColor = field(init=False, default=QtGui.QColor.fromHsl(29, 255, 127))

    def __post_init__(self):
        pass

    def as_qpoints(self, image: QtWidgets.QLabel, cap_width: int, cap_height: int):
        sfw = cap_width / image.width()
        sfh = cap_height / image.height()
        return [QtCore.QPoint(c[0, 0] // sfw, c[0, 1] // sfh) for c in self.contour]
