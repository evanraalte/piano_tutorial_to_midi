from modules.midi_converter import MidiConverter
from modules.video_config import VideoConfig
import cv2

config = VideoConfig.from_yaml("config.yaml")
midi_converter = MidiConverter(config, generate_masks=True)
while not midi_converter.is_completed:
    frame = midi_converter.process_frame()
    cv2.imshow("Preview", frame)
    cv2.waitKey(1)
midi_converter.save("song.mid")

