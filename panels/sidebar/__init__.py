from .base import Panel, PanelConstructor, PanelWidget
from .widgets.color_pick import WidgetColorPick
from .widgets.frame_select import WidgetFrameSelect
from .widgets.start_note import WidgetStartNote
from .widgets.video_select import WidgetVideoSelect
from .widgets.conversion import WidgetConversion

from enum import Enum


class AvailablePanels(Enum):
    file_select = PanelConstructor(
        description="Select a video file to open. You can also download a youtube video and then select it.",
        widget=WidgetVideoSelect,
    )
    frame_select = PanelConstructor(
        description="Select a frame that contains the keys you want to include",
        widget=WidgetFrameSelect,
    )
    start_note = PanelConstructor(
        description="The start note should be selected already (if you frame selection was larger than 11 notes). As the selection pertains only relative notes, you need to select the octave to start on.",
        widget=WidgetStartNote,
    )
    color_pick = PanelConstructor(
        description="Select the colors that represent the key presses, you can scrub through the video to find them",
        widget=WidgetColorPick,
    )
    start_conversion = PanelConstructor(
        description="Convert your song to midi!",
        widget=WidgetConversion,
        button_next_text="Start conversion",
    )
