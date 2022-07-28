import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore

from Noterator import Notes
from functools import partial
from Color import Color
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class StartNoteSelector(QtWidgets.QWidget):
    signal_start_note_updated = QtCore.Signal(Notes)

    def __init__(self):
        super(StartNoteSelector, self).__init__()
        layout = QtWidgets.QGridLayout()
        self.buttons = {note: QtWidgets.QPushButton(note.name, self) for note in Notes}
        for note, button in self.buttons.items():
            button.setFixedWidth(20)
            button.setAutoFillBackground(True)
            button.clicked.connect(partial(self.clicked, note))
            layout.addWidget(button, 1, note.value, 1, 1)
        self.dummy = Color("Blue")
        layout.addWidget(self.dummy, 2, 0, 1, len(self.buttons))
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def clicked(self, clicked_note):
        for note, button in self.buttons.items():
            pal = QtWidgets.QPushButton().palette()
            if note == clicked_note:
                pal.setColor(QtGui.QPalette.Button, "Green")
            button.setPalette(pal)
            button.update()
        self.signal_start_note_updated.emit(clicked_note)
