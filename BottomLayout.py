import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore

from VideoPlayer import VideoPlayer
from VideoEditPanel import VideoEditPanel
from FrameMode import FrameMode

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class BottomLayout(QtWidgets.QWidget):
    def __init__(self):
        super(BottomLayout, self).__init__()
        layout = QtWidgets.QHBoxLayout()

        self.video_player = VideoPlayer()
        layout.addWidget(self.video_player)

        self.video_edit_panel = VideoEditPanel()

        self.video_edit_panel.btn_frame_select.clicked.connect(
            lambda x: self.video_player.set_mode(FrameMode.FRAME_SELECT)
        )

        self.video_edit_panel.color_picker.signal_clicked.connect(
            lambda: self.video_player.set_mode(FrameMode.COLOR_PICK)
        )
        self.video_player.image_label.signal_color_picked.connect(self.video_edit_panel.color_picker.pick_color)

        layout.addWidget(self.video_edit_panel)
        self.video_player.video_analyzer.signal_start_note_updated.connect(
            lambda x: self.video_edit_panel.start_note_selector.clicked(x)
        )
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.video_player.load_video("Downloads/Speech Bubbles - The Smile [Piano Cover].mp4")
