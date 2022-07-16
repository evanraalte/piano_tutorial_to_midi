import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore
from ..base import PanelWidget

from functools import partial

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class WidgetColorPick(PanelWidget):
    signal_color_button_clicked = QtCore.Signal()
    signal_color_selected = QtCore.Signal()

    def __init__(self):
        super(WidgetColorPick, self).__init__()
        self.create_view()
        self.colors = {}

    def create_view(self):
        self.layout = QtWidgets.QHBoxLayout()
        self.labels = [f"{hand}_{key}" for hand in ("left", "right") for key in ("black", "white")]
        self.color_picked = {}
        self.btns_color_pick = {}
        for label in self.labels:
            btn = QtWidgets.QPushButton(label)
            btn.clicked.connect(partial(self.set_active_button, label))
            btn.setAutoFillBackground(True)
            btn.clicked.connect(self.signal_color_button_clicked)
            self.layout.addWidget(btn)
            self.btns_color_pick[label] = btn
        self.setLayout(self.layout)

    def reset_view(self):
        for label in self.labels:
            self.color_picked[label] = False
            btn = self.btns_color_pick[label]
            pal = QtWidgets.QPushButton().palette()
            btn.setPalette(pal)
            btn.update()

    def set_active_button(self, button_name):
        self.active_button = button_name
        logger.info(self.active_button)

    def pick_color(self, color: QtGui.QColor):
        btn = self.btns_color_pick[self.active_button]
        pal = btn.palette()
        pal.setColor(QtGui.QPalette.Button, color)
        btn.setPalette(pal)
        btn.update()
        self.color_picked[self.active_button] = color
        logger.info(f"Set color of {self.active_button} to {color}")
        self.button_next.setEnabled(all(self.color_picked.values()))
