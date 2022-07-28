import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class LabelWithRubberband(QtWidgets.QLabel):
    signal_selection_complete = QtCore.Signal(QtCore.QPoint, QtCore.QPoint)

    def __init__(self):
        super(LabelWithRubberband, self).__init__()
        self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)

    def mousePressEvent(self, event):

        self.origin = event.pos()
        logger.info(self.origin)
        self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        self.rubberBand.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        self.end_point = event.pos()
        logger.info(event.pos())
        self.signal_selection_complete.emit(self.end_point, self.origin)
        self.rubberBand.hide()
