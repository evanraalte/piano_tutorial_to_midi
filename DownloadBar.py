from pathlib import Path
from typing import BinaryIO
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QProgressBar,
    QComboBox,
)
from PySide6.QtCore import Signal
from Color import Color
from pytube import YouTube
from pytube.helpers import RegexMatchError
from pytube.exceptions import VideoUnavailable
import logging
from threading import Thread


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class DownloadBar(QWidget):
    signal_download_complete = Signal(str)
    signal_download_on_progress = Signal(str)
    DOWNLOAD_PATH = Path("Downloads")

    def __init__(self):
        super(DownloadBar, self).__init__()

        layout_row0 = QHBoxLayout()
        self.line_edit_url = QLineEdit()
        self.line_edit_url.textEdited.connect(self.fetch_info)
        self.line_edit_url.setText("")
        layout_row0.addWidget(self.line_edit_url)

        self.combo_box_quality = QComboBox()
        self.combo_box_quality.setMinimumWidth(100)
        self.combo_box_quality.setDisabled(True)
        layout_row0.addWidget(self.combo_box_quality)

        self.button_download = QPushButton(text="Download", parent=self)
        self.button_download.clicked.connect(self.download)
        self.button_download.setEnabled(False)
        layout_row0.addWidget(self.button_download)

        layout_row1 = QHBoxLayout()
        self.label_video_title = QLabel()
        layout_row1.addWidget(QLabel("Title:"))
        layout_row1.addWidget(self.label_video_title)
        layout_row1.setContentsMargins(0, 0, 0, 0)

        layout_row2 = QHBoxLayout()
        self.progress_bar = QProgressBar()
        layout_row2.addWidget(self.progress_bar)
        layout_row2.setContentsMargins(0, 0, 0, 0)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(layout_row0)
        layout.addLayout(layout_row1)
        layout.addLayout(layout_row2)
        self.setLayout(layout)

    def fetch_info(self):
        try:
            self.yt = YouTube(
                url=self.line_edit_url.text(),
                on_progress_callback=self.cb_on_progress,
                on_complete_callback=self.cb_on_complete,
            )
            self.streams = [
                s
                for s in self.yt.streams.filter(file_extension="mp4")
                if hasattr(s, "resolution") and s.type == "video"
            ]
            self.label_video_title.setText(self.yt.title)
            self.combo_box_quality.clear()
            for s in self.streams:
                self.combo_box_quality.addItem(f"{s.resolution} / {s.fps}", s.itag)
            self.button_download.setEnabled(True)
            self.combo_box_quality.setEnabled(True)
        except (RegexMatchError, VideoUnavailable):
            self.combo_box_quality.clear()
            self.combo_box_quality.setEnabled(False)
            self.button_download.setEnabled(False)
            self.label_video_title.setText("")
            logger.debug("Invalid URL!")

    def cb_on_progress(self, chunk: bytes, file_handler: BinaryIO, bytes_remaining: int):
        self.signal_download_on_progress.emit()
        bytes_done = self.stream.filesize - bytes_remaining
        percent_done = (bytes_done / self.stream.filesize) * 100
        logger.info(f"on_progress: {percent_done:.2f}")
        self.progress_bar.setValue(int(percent_done))

    def cb_on_complete(self, stream, file_path: str):
        self.signal_download_complete.emit(file_path)
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
