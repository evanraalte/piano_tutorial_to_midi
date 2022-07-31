import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore

from StartNoteSelector import StartNoteSelector
from Noterator import Noterator
from functools import partial
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ColorPickPanel(QtWidgets.QFrame):
    signal_clicked = QtCore.Signal()

    def __init__(self, labels: list[str]):
        super(ColorPickPanel, self).__init__()
        layout = QtWidgets.QVBoxLayout()
        btn_layout = QtWidgets.QHBoxLayout()
        self.btns_color_pick = {}
        for label in labels:
            btn = QtWidgets.QPushButton(label)
            btn.clicked.connect(partial(self.set_active_button, label))
            btn.setAutoFillBackground(True)
            btn.clicked.connect(self.signal_clicked)
            btn_layout.addWidget(btn)
            self.btns_color_pick[label] = btn

        layout.addWidget(QtWidgets.QLabel("Color picker"))
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.setFrameStyle(QtWidgets.QFrame.Box)

    def set_active_button(self, button_name):
        self.active_button = button_name
        logger.info(self.active_button)

    def pick_color(self, color: QtGui.QColor):
        btn = self.btns_color_pick[self.active_button]
        pal = btn.palette()
        pal.setColor(QtGui.QPalette.Button, color)
        btn.setPalette(pal)
        btn.update()


class CheckBoxPanel(QtWidgets.QFrame):
    def __init__(self, labels: list[str]):
        super(CheckBoxPanel, self).__init__()
        layout = QtWidgets.QVBoxLayout()
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.check_boxes = {label: QtWidgets.QCheckBox(label) for label in labels}
        for cb in self.check_boxes.values():
            cb.setEnabled(False)
            layout.addWidget(cb)
        self.setLayout(layout)
        self.setFrameStyle(QtWidgets.QFrame.Box)


class VideoEditPanel(QtWidgets.QWidget):
    def __init__(self):
        super(VideoEditPanel, self).__init__()
        layout = QtWidgets.QVBoxLayout()

        self.btn_frame_select = QtWidgets.QPushButton("Select frame in image")
        layout.addWidget(self.btn_frame_select)

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

        self.color_picker = ColorPickPanel(
            [f"{hand}_{key}" for hand in ("left", "right") for key in ("black", "white")]
        )
        layout.addWidget(self.color_picker)

        self.check_box_panel = CheckBoxPanel(["select_frame", "set_start_note", "pick_colors"])
        layout.addWidget(self.check_box_panel)

        # spacer = QtWidgets.QSpacerItem(0, 0, vData=QtWidgets.QSizePolicy.Maximum)
        # layout.addSpacerItem(spacer)

        self.btn_start_conversion = QtWidgets.QPushButton("Start conversion")
        layout.addWidget(self.btn_start_conversion)
        self.setLayout(layout)

    def update_combo_box_midi_notes(self, note):
        available_notes = [n for n in Noterator() if n.note == note]
        self.combo_box_midi_notes.clear()
        for n in available_notes:
            self.combo_box_midi_notes.addItem(str(n), n)
        pass
