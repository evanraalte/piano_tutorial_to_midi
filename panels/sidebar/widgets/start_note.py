import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore
from ..base import PanelWidget
from modules.note_tools import Notes, NoteIterator
from functools import partial

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class StartNoteSelector(QtWidgets.QWidget):
    signal_start_note_updated = QtCore.Signal(Notes)
    # https://stackoverflow.com/questions/38383632/how-to-properly-size-qt-widgets
    def __init__(self):
        super(StartNoteSelector, self).__init__()
        layout = QtWidgets.QGridLayout()
        self.buttons = {note: QtWidgets.QPushButton(note.name, self) for note in Notes}
        for note, button in self.buttons.items():
            button.setFixedWidth(20)
            button.setAutoFillBackground(True)
            button.clicked.connect(partial(self.clicked, note))
            layout.addWidget(button, 1, note.value, 1, 1)
        # self.dummy = Color("Blue")
        # layout.addWidget(self.dummy, 2, 0, 1, len(self.buttons))
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def reset_view(self):
        for note, button in self.buttons.items():
            pal = QtWidgets.QPushButton().palette()
            button.setPalette(pal)
            button.update()

    def clicked(self, clicked_note):
        for note, button in self.buttons.items():
            pal = QtWidgets.QPushButton().palette()
            if note == clicked_note:
                pal.setColor(QtGui.QPalette.Button, "Green")
            button.setPalette(pal)
            button.update()
        self.signal_start_note_updated.emit(clicked_note)
        self.clicked_note = clicked_note


class WidgetStartNote(PanelWidget):
    def create_view(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.lbl_start_note = QtWidgets.QLabel("Selected start note:")
        self.lbl_start_note.setFixedHeight(12)
        self.layout.addWidget(self.lbl_start_note)

        self.start_note_selector = StartNoteSelector()
        self.layout.addWidget(self.start_note_selector)

        self.lbl_midi_start_note = QtWidgets.QLabel("Midi start note:")
        self.lbl_midi_start_note.setFixedHeight(12)
        self.layout.addWidget(self.lbl_midi_start_note)

        self.combo_box_midi_notes = QtWidgets.QComboBox()
        self.layout.addWidget(self.combo_box_midi_notes)
        self.start_note_selector.signal_start_note_updated.connect(self.update_combo_box_midi_notes)
        self.start_note_selector.signal_start_note_updated.connect(lambda x: self.button_next.setEnabled(True))
        self.layout.addWidget(self.start_note_selector)
        self.setLayout(self.layout)

    def reset_view(self):
        self.combo_box_midi_notes.clear()
        self.start_note_selector.reset_view()

    def __init__(self):
        super(WidgetStartNote, self).__init__()
        self.create_view()

    def start_note_found(self, start_note):
        self.start_note_selector.clicked(start_note)

    def update_combo_box_midi_notes(self, note):
        available_notes = [n for n in NoteIterator() if n.note == note]
        self.combo_box_midi_notes.clear()
        for n in available_notes:
            self.combo_box_midi_notes.addItem(str(n), n)
