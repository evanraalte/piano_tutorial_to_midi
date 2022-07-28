import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout
from Color import Color
from DownloadBar import DownloadBar
import logging

from VideoPlayer import BottomLayout

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%S",
)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("My App")

        layout = QGridLayout()
        self.download_bar = DownloadBar()
        self.bottom_layout = BottomLayout()
        # Glue
        # self.download_bar.signal_download_complete.connect(self.bottom_layout.video_player.load_video)

        layout.addWidget(self.download_bar, 0, 0, 1, 3)
        # layout.addWidget(Color('green'), 0, 3)
        layout.addWidget(self.bottom_layout, 1, 0, 3, 3)
        # layout.addWidget(Color("purple"), 2, 1)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
