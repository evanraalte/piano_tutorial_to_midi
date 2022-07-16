import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore

from modules.frame_mode import FrameMode

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class LabelWithRubberband(QtWidgets.QLabel):
    signal_selection_complete = QtCore.Signal(QtCore.QPoint, QtCore.QPoint)
    signal_color_picked = QtCore.Signal(QtGui.QColor)
    signal_mode_updated = QtCore.Signal(FrameMode)

    def __init__(self):
        super(LabelWithRubberband, self).__init__()
        self.mode = FrameMode.IDLE
        self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)

    def mousePressEvent(self, event):

        self.origin = event.pos()
        logger.info(self.origin)

        match self.mode:
            case FrameMode.FRAME_SELECT:
                self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
                self.rubberBand.show()
        pass

    def mouseMoveEvent(self, event):
        match self.mode:
            case FrameMode.FRAME_SELECT:
                self.rubberBand.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode: FrameMode):
        self._mode = mode
        self.signal_mode_updated.emit(self._mode)

    def mouseReleaseEvent(self, event):
        match self.mode:
            case FrameMode.FRAME_SELECT:
                self.end_point = event.pos()
                logger.info(event.pos())
                self.signal_selection_complete.emit(self.end_point, self.origin)
                self.rubberBand.hide()
            case FrameMode.COLOR_PICK:
                image = self.pixmap().toImage()
                pixel = QtGui.QColor(image.pixel(self.origin))
                self.signal_color_picked.emit(pixel)
        self.mode = FrameMode.IDLE
