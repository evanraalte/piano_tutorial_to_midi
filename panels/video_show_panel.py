from tkinter import Frame
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore
from modules.video_player import VideoPlayer
from panels.sidebar.widgets.color_pick import WidgetColorPick
from panels.sidebar.widgets.start_note import WidgetStartNote
from panels.sidebar.widgets.conversion import WidgetConversion
from panels.video_edit_panel import AvailablePanels, VideoEditPanel
from modules.frame_mode import FrameMode
from modules.video_config import VideoConfig
from modules.midi_converter import MidiConverter
import yaml
import logging
import numpy as np
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class VideoShowPanel(QtWidgets.QWidget):
    signal_test = QtCore.Signal(np.ndarray)
    def action_video_load(self):
        file = self.video_edit_panel.get_panel(AvailablePanels.file_select).widget.file
        self.video_player.load_video(file)

    def actions_frame_select_clicked(self):
        self.video_player.set_mode(FrameMode.FRAME_SELECT)
        self.video_player.draw_contour_overlay([])  # TODO: should erase the saved contours

    def action_conversion(self):
        widget_start_note: WidgetStartNote = self.video_edit_panel.get_panel(AvailablePanels.start_note).widget
        widget_color_pick: WidgetColorPick = self.video_edit_panel.get_panel(AvailablePanels.color_pick).widget
        widget_start_conversion: WidgetConversion = self.video_edit_panel.get_panel(AvailablePanels.start_conversion).widget

        # generate a yaml file
        video_config = VideoConfig(
            video_file=self.video_player.video_path,
            key_contours=[contour.contour for contour in self.video_player.contours],
            key_colors=widget_color_pick.color_picked,
            midi_start_note=widget_start_note.combo_box_midi_notes.currentData().midi_num,
        )
        widget_start_conversion.button_next.setEnabled(False)
        widget_start_conversion.button_file_select.setEnabled(False)
        self.video_player.set_mode(FrameMode.CONVERTING)
        video_config.to_yaml("config.yaml")
        # video_config = VideoConfig.from_yaml("config.yaml")
        midi_converter = MidiConverter(video_config, generate_masks=True)
        while not midi_converter.is_completed:
            midi_converter.process_frame()
            if widget_start_conversion.checkbox_live_update.isChecked():
                self.video_player.frame_slider.setValue(midi_converter.frame_num)
            logger.info(f"{midi_converter.frame_num} / {midi_converter.frames_total}")
            QtCore.QCoreApplication.processEvents()
        midi_converter.save(widget_start_conversion.destination_path)
        self.video_player.set_mode(FrameMode.IDLE)
        widget_start_conversion.button_next.setEnabled(True)
        widget_start_conversion.button_file_select.setEnabled(True)
        pass


    def __init__(self):
        super(VideoShowPanel, self).__init__()
        layout = QtWidgets.QHBoxLayout()

        

        self.video_player = VideoPlayer()
        layout.addWidget(self.video_player)

        self.video_edit_panel = VideoEditPanel()
        layout.addWidget(self.video_edit_panel)

        self.video_edit_panel.get_panel(AvailablePanels.file_select).signal_button_next_clicked.connect(
            self.action_video_load
        )
        self.video_player.signal_video_loaded.connect(self.video_edit_panel.actions_loaded_video)
        self.video_edit_panel.signal_frame_select_clicked.connect(self.actions_frame_select_clicked)

        self.video_player.signal_frame_selected.connect(self.video_edit_panel.actions_selected_frame)

        self.video_player.video_analyzer.signal_start_note_updated.connect(
            self.video_edit_panel.actions_start_note_selected
        )

        self.video_edit_panel.get_panel(AvailablePanels.color_pick).widget.signal_color_button_clicked.connect(
            lambda: self.video_player.set_mode(FrameMode.COLOR_PICK)
        )
        self.video_player.image_label.signal_color_picked.connect(
            self.video_edit_panel.get_panel(AvailablePanels.color_pick).widget.pick_color
        )

        self.video_edit_panel.get_panel(AvailablePanels.start_conversion).signal_button_next_clicked.connect(
            self.action_conversion
        )
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
