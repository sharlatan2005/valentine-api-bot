from enum import IntEnum, auto

class States(IntEnum):
    SELECTING_RECIPIENT = auto()
    GENERATING_IMAGE = auto()
    EDITING_IMAGE = auto()
    GENERATING_TEXT = auto()
    EDITING_TEXT = auto()
    CONFIRMING = auto()