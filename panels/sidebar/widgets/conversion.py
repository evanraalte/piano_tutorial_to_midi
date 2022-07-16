import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore
from ..base import PanelWidget
from pytube import YouTube
from pytube.helpers import RegexMatchError
from pytube.exceptions import VideoUnavailable
from pathlib import Path
from threading import Thread
import os
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class WidgetConversion(PanelWidget):
    MAX_LABEL_LENGTH = 40

    def create_view(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(QtWidgets.QLabel("Select destination file"))
        self.button_file_select = QtWidgets.QPushButton("Select file")
        self.button_file_select.released.connect(self.save_as)
        self.layout.addWidget(self.button_file_select)
        self.label_file_selected = QtWidgets.QLabel("")
        self.layout.addWidget(self.label_file_selected)

        self.checkbox_live_update = QtWidgets.QCheckBox("Update GUI during conversion")
        self.checkbox_live_update.setChecked(True)
        self.layout.addWidget(self.checkbox_live_update)
        self.setLayout(self.layout)

    def save_as(self):
        # file_name = QtWidgets.QFileDialog.getSaveFileName(self, "Save file", "", filter="Midi files (*.mid)")
        # pass
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setNameFilter("Midi files (*.mid)")
        dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dialog.setDefaultSuffix(".mid")
        dialog.selectFile("output")
        if dialog.exec_():
            self.destination_path = Path(dialog.selectedFiles()[0])
            self.label_file_selected.setText(f"{self.destination_path}")
            self.button_next.setEnabled(True)
            pass

    def reset_view(self):
        pass

    def __init__(self):
        super(WidgetConversion, self).__init__()
        self.create_view()
        self.reset_view()
