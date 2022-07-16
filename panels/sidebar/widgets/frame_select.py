import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore
from ..base import PanelWidget

from functools import partial

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class WidgetFrameSelect(PanelWidget):
    def __init__(self):
        super(WidgetFrameSelect, self).__init__()
        self.create_view()

    def create_view(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.button_frame_select = QtWidgets.QPushButton("")
        self.layout.addWidget(self.button_frame_select)
        self.button_frame_select.clicked.connect(partial(self.set_widget_state, True))
        self.setLayout(self.layout)

    def reset_view(self):
        self.set_widget_state(frame_select_mode=False)

    def set_widget_state(self, frame_select_mode: bool):
        if frame_select_mode:
            print(id(self))
            self.button_frame_select.setText("Drag a frame in the image on the left...")
            self.button_frame_select.setEnabled(False)
        else:
            self.button_frame_select.setText("(Re)select a frame")
            self.button_frame_select.setEnabled(True)
