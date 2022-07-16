import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout
import logging

from panels.video_show_panel import VideoShowPanel

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
        self.video_show_panel = VideoShowPanel()
        layout.addWidget(self.video_show_panel, 1, 0, 3, 3)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
