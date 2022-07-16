import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout
from Color import Color
from DownloadBar import DownloadBar
class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("My App")

        layout = QGridLayout()

        layout.addWidget(DownloadBar(), 0, 0, 1, 3)
        # layout.addWidget(Color('green'), 0, 3)
        layout.addWidget(Color('blue'), 1, 1)
        layout.addWidget(Color('purple'), 2, 1)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()