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


class WidgetVideoSelect(PanelWidget):
    MAX_LABEL_LENGTH = 40
    DOWNLOAD_PATH = Path("Downloads")

    def create_view(self):
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(
            QtWidgets.QLabel(f"[Optional] Fetch vid from YouTube (to {self.DOWNLOAD_PATH}/):"), 0, 0, 1, 4
        )
        self.editbox_url = QtWidgets.QLineEdit()
        self.editbox_url.textEdited.connect(self.check_url)
        self.layout.addWidget(self.editbox_url, 1, 0, 1, 2)
        self.combo_box_quality = QtWidgets.QComboBox()
        self.combo_box_quality.setMinimumWidth(100)
        self.combo_box_quality.setEnabled(False)
        self.layout.addWidget(self.combo_box_quality, 1, 2, 1, 1)
        self.button_download = QtWidgets.QPushButton("Download")
        self.button_download.released.connect(self.download)
        self.button_download.setEnabled(False)
        self.layout.addWidget(self.button_download, 1, 3, 1, 1)
        self.layout.addWidget(QtWidgets.QLabel("Select a file to analyze:"), 2, 0, 1, 4)
        self.button_file_select = QtWidgets.QPushButton("Select file")
        self.button_file_select.released.connect(self.open_file)
        self.layout.addWidget(self.button_file_select, 3, 0, 1, 1)
        self.label_file_selected = QtWidgets.QLabel("")
        self.layout.addWidget(self.label_file_selected, 3, 1, 1, 3)
        self.setLayout(self.layout)
        self.setContentsMargins(0, 0, 0, 0)

    def open_file(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, "Open video", os.getcwd(), "Video files (*.mp4)")
        self.file = Path(file_path[0]).relative_to(os.getcwd())
        file_label = (
            str(self.file)[0 : self.MAX_LABEL_LENGTH - 3] + "..."
            if len(str(self.file)) > self.MAX_LABEL_LENGTH
            else str(self.file)
        )
        self.label_file_selected.setText(f"{file_label}")
        self.button_next.setEnabled(True)
        pass

    def check_url(self):

        try:
            self.yt = YouTube(
                url=self.editbox_url.text(),
                on_progress_callback=self.cb_on_progress,
                on_complete_callback=self.cb_on_complete,
            )
            self.streams = [
                s
                for s in self.yt.streams.filter(file_extension="mp4")
                if hasattr(s, "resolution") and s.type == "video"
            ]
            self.combo_box_quality.clear()
            for s in self.streams:
                self.combo_box_quality.addItem(f"{s.resolution} / {s.fps}", s.itag)
            self.button_download.setEnabled(True)
            self.combo_box_quality.setEnabled(True)
        except (RegexMatchError, VideoUnavailable):
            self.combo_box_quality.clear()
            self.combo_box_quality.setEnabled(False)
            self.button_download.setEnabled(False)
            logger.debug("Invalid URL!")

    def cb_on_progress(self, chunk: bytes, file_handler, bytes_remaining: int):
        bytes_done = self.stream.filesize - bytes_remaining
        progress = bytes_done / self.stream.filesize
        self.set_editbox_url_progress(progress)

    def cb_on_complete(self, stream, file_path: str):
        logger.info(f"Saved file to {file_path}")

    def download(self):
        logger.info(f"Downloading...")

        self.DOWNLOAD_PATH.mkdir(exist_ok=True)
        itag = self.combo_box_quality.currentData()
        self.stream = self.yt.streams.get_by_itag(itag)
        download_thread = Thread(
            target=lambda: self.stream.download(skip_existing=False, output_path=self.DOWNLOAD_PATH)
        )
        download_thread.start()
        pass

    def set_editbox_url_progress(self, value):
        QRectF = QtCore.QRectF(self.editbox_url.rect())
        palette = self.editbox_url.palette()
        gradient = QtGui.QLinearGradient(QRectF.topLeft(), QRectF.topRight())
        gradient.setColorAt(value - 0.002, QtGui.QColor("green"))
        gradient.setColorAt(value - 0.001, QtGui.QColor("#ffffff"))
        gradient.setColorAt(value, QtGui.QColor("#ffffff"))
        palette.setBrush(QtGui.QPalette.Base, QtGui.QBrush(gradient))
        self.editbox_url.setPalette(palette)

    def reset_view(self):
        pass

    def __init__(self):
        super(WidgetVideoSelect, self).__init__()
        self.create_view()
