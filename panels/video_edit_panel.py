from enum import Enum
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore
from functools import partial
import logging

from panels.sidebar import Panel, AvailablePanels
from panels.sidebar import WidgetStartNote

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class VideoEditPanel(QtWidgets.QWidget):
    signal_frame_select_clicked = QtCore.Signal()

    def set_active_panel(self, panel: AvailablePanels):
        for panel_name in self.panels:
            if panel_name == panel.name:
                self.panels[panel_name].setEnabled(True)
            else:
                self.panels[panel_name].setEnabled(False)

    def create_view(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.panels = {p.name: Panel(p.value) for p in AvailablePanels}
        panel_names = list(self.panels.keys())
        for panel_name, panel in self.panels.items():
            panel.setEnabled(False)
            self.layout.addWidget(panel)
            try:
                next_panel = AvailablePanels[panel_names[panel_names.index(panel_name) + 1]]
                panel.button_next.released.connect(partial(self.set_active_panel, next_panel))
            except IndexError:
                pass  # The last button can not be connected to another one
        # Connect signals
        self.get_panel(AvailablePanels.frame_select).widget.button_frame_select.clicked.connect(
            self.signal_frame_select_clicked
        )
        print(id(self.get_panel(AvailablePanels.frame_select).widget))
        self.setLayout(self.layout)

    def reset_view(self):
        for _, panel in self.panels.items():
            panel.reset_view()
            panel.setEnabled(False)
        self.set_active_panel(AvailablePanels.file_select)

    def get_panel(self, panel: AvailablePanels) -> Panel:
        return self.panels[panel.name]

    def actions_loaded_video(self):
        self.reset_view()
        self.set_active_panel(AvailablePanels.frame_select)

    def actions_selected_frame(self):
        panel_frame_select = self.get_panel(AvailablePanels.frame_select)
        panel_frame_select.button_next.setEnabled(True)
        panel_frame_select.widget.set_widget_state(False)

    def actions_start_note_selected(self, start_note):
        widget: WidgetStartNote = self.get_panel(AvailablePanels.start_note).widget
        widget.start_note_found(start_note)

    def __init__(self):
        super(VideoEditPanel, self).__init__()
        self.create_view()
        self.reset_view()
