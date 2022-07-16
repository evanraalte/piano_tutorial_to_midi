from typing import BinaryIO
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel,QVBoxLayout, QProgressBar
from Color import Color
from pytube import YouTube
from pytube.helpers import  RegexMatchError
from pytube.exceptions import VideoUnavailable


class DownloadBar(QWidget):
    def __init__(self):
        super(DownloadBar, self).__init__()

        layout_row0 = QHBoxLayout()
        self.line_edit_url = QLineEdit()
        self.line_edit_url.textEdited.connect(self.fetch_info)
        self.line_edit_url.setText("")
        layout_row0.addWidget(self.line_edit_url)

        self.button_download = QPushButton(text="Download", parent=self)
        self.button_download.clicked.connect(self.download)
        self.button_download.setEnabled(False)
        layout_row0.addWidget(self.button_download)



        layout_row1 = QHBoxLayout()
        self.label_video_title = QLabel()
        layout_row1.addWidget(QLabel("Title:"))
        layout_row1.addWidget(self.label_video_title)
        layout_row1.setContentsMargins(0,0,0,0)

        layout_row2 = QHBoxLayout()
        self.progress_bar = QProgressBar()
        layout_row2.addWidget(self.progress_bar)
        layout_row2.setContentsMargins(0,0,0,0)

        
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addLayout(layout_row0)
        layout.addLayout(layout_row1)
        layout.addLayout(layout_row2)
        self.setLayout(layout)



    def fetch_info(self):
        try:
            self.yt = YouTube(url=self.line_edit_url.text())
            self.label_video_title.setText(self.yt.title)
            self.button_download.setEnabled(True)
        except (RegexMatchError, VideoUnavailable):
            self.button_download.setEnabled(False)
            self.label_video_title.setText("")
            print("Invalid URL!")

    def cb_on_progress(self, chunk: bytes, file_handler: BinaryIO, bytes_remaining: int):
        bytes_done = self.stream.filesize - bytes_remaining
        percent_done =(bytes_done/self.stream.filesize)*100
        print(f"on_progress: {percent_done:.2f}")
        self.progress_bar.setValue(int(percent_done))

    @staticmethod
    def cb_on_complete():
        pass

    def download(self):
        print(f"Downloading...")
        self.stream = self.yt.streams.filter(file_extension="mp4",res="1080p").first()
        self.yt.register_on_progress_callback(self.cb_on_progress)
        self.stream.download(skip_existing=False)
        pass
        
