from enum import Enum, auto


class FrameMode(Enum):
    IDLE = auto()
    COLOR_PICK = auto()
    FRAME_SELECT = auto()
    CONVERTING = auto()
