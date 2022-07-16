from __future__ import annotations
from dataclasses import dataclass
from PySide6 import QtGui
from pathlib import Path
import yaml
import numpy as np


@dataclass
class VideoConfig:
    key_contours: list[np.array]
    video_file: Path
    key_colors: dict[str, QtGui.QColor]
    midi_start_note: int

    def as_dict(self) -> dict:
        yaml_dict = {}
        yaml_dict["key_contours"] = [contour.tolist() for contour in self.key_contours]
        yaml_dict["video_file"] = str(self.video_file.absolute())
        yaml_dict["key_colors"] = {key: color.rgb() for key, color in self.key_colors.items()}
        yaml_dict["midi_start_note"] = self.midi_start_note
        return yaml_dict

    @classmethod
    def from_yaml(cls, source_file: Path | str) -> VideoConfig:
        source_file = Path(source_file)
        with source_file.open() as f:
            yaml_dict = yaml.load(f, Loader=yaml.Loader)
        # conversion to correct datatype
        yaml_dict["key_contours"] = [np.array(contour) for contour in yaml_dict["key_contours"]]
        yaml_dict["video_file"] = Path(yaml_dict["video_file"])
        yaml_dict["key_colors"] = {key: QtGui.QColor.fromRgb(color) for key, color in yaml_dict["key_colors"].items()}
        return cls(**yaml_dict)

    def to_yaml(self, destination_file: Path | str):
        destination_file = Path(destination_file)
        with destination_file.open("w") as f:
            yaml.dump(self.as_dict(), f)
        pass
