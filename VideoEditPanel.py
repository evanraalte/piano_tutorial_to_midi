import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore

from StartNoteSelector import StartNoteSelector
from Noterator import Noterator
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class VideoEditPanel(QtWidgets.QWidget):
    def __init__(self):
        super(VideoEditPanel, self).__init__()
        layout = QtWidgets.QVBoxLayout()

        self.lbl_start_note = QtWidgets.QLabel("Selected start note:")
        self.lbl_start_note.setFixedHeight(12)
        layout.addWidget(self.lbl_start_note)

        self.start_note_selector = StartNoteSelector()
        layout.addWidget(self.start_note_selector)

        self.lbl_midi_start_note = QtWidgets.QLabel("Midi start note:")
        self.lbl_midi_start_note.setFixedHeight(12)
        layout.addWidget(self.lbl_midi_start_note)

        self.combo_box_midi_notes = QtWidgets.QComboBox()
        layout.addWidget(self.combo_box_midi_notes)
        self.start_note_selector.signal_start_note_updated.connect(self.update_combo_box_midi_notes)
        layout.addWidget(self.start_note_selector)
        self.setLayout(layout)

    def update_combo_box_midi_notes(self, note):
        available_notes = [n for n in Noterator() if n.note == note]
        self.combo_box_midi_notes.clear()
        for n in available_notes:
            self.combo_box_midi_notes.addItem(str(n), n)
        pass
