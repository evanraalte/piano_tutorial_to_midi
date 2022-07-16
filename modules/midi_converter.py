from dataclasses import dataclass
import functools
from typing import Callable
from modules.video_config import VideoConfig
import cv2
import numpy as np
import mido

@dataclass
class MidiConverter:
    TRACKS = ["left", "right"]
    # Maximum deviations for HSL color matching
    H_DEV = 10 # Hue
    S_DEV = 60 # Saturation
    L_DEV = 60 # Lightness

    config: VideoConfig
    generate_masks: bool = False

    def __post_init__(self):
        self.cap = cv2.VideoCapture(str(self.config.video_file))
        self.tracks = {track: mido.MidiTrack() for track in self.TRACKS}
        self.frames_since_last_midi_message = {track: 0 for track in self.TRACKS}
        self.mid = mido.MidiFile()
        self.mid.tracks.append(self.tracks["left"])
        self.mid.tracks.append(self.tracks["right"])

        # Generate masks
        ret, frame = self.cap.read()
        self.masks = {}
        for key_num, contour in enumerate(self.config.key_contours):
            self.masks[key_num] = np.zeros(frame.shape[:2], np.uint8)
            cv2.drawContours(self.masks[key_num], [contour], -1, 255, -1)

        self.pressed_key_state = set()

    def matches_reference_key_color(self, piano_key_num: int, piano_key_color: tuple[int, int, int, int]) -> tuple[str, int] | None:
        for piano_key_type, piano_key_reference_color in self.config.key_colors.items():
            # Check whether a piano key matches the reference key color
            h, s, l, _ = piano_key_reference_color.getHsl()
            if all(
                cv2.inRange(
                    piano_key_color,  # mean of masked area
                    (h / 2 - self.H_DEV, l - self.L_DEV, s - self.S_DEV, 0),  # lower bound
                    (h / 2 + self.H_DEV, l + self.L_DEV, s + self.S_DEV, 0),  # `upper bound
                )
            ):
                    hand = "left" if "left" in piano_key_type else "right"
                    return (piano_key_num, hand)
        return None

    def update_state(self, pressed_keys, frame_num):
        time_delta = {}
        note_on = pressed_keys.difference(self.pressed_key_state)
        note_off = self.pressed_key_state.difference(pressed_keys)
        self.pressed_key_state = pressed_keys
        # Update delta time
        for hand in self.TRACKS:
            if hand in [v for k,v in note_on|note_off]:
                time_delta[hand] = int(1000 * (frame_num-self.frames_since_last_midi_message[hand]) / self.cap.get(cv2.CAP_PROP_FPS))
                self.frames_since_last_midi_message[hand] = frame_num
                

        for (key, hand )in note_on:
            self.tracks[hand].append(mido.Message('note_on', note=self.config.midi_start_note + key, velocity=60, time=time_delta[hand]))
            print(f"note_on: {hand=} {key=} {time_delta[hand]=} {frame_num=}")
            time_delta[hand] = 0
        for (key, hand )in note_off:
            self.tracks[hand].append(mido.Message('note_off', note=self.config.midi_start_note + key, velocity=60, time=time_delta[hand]))
            print(f"note_off: {hand=} {key=} {time_delta[hand]=} {frame_num=}")
            time_delta[hand] = 0
        pass

    @property
    def is_completed(self):
        return self.frame_num == self.frames_total

    @property
    def frame_num(self):
        return self.cap.get(cv2.CAP_PROP_POS_FRAMES)

    @property
    def frames_total(self):
        return self.cap.get(7)

    def save(self, name):
        self.mid.save(name)

    def process_frame(self):
        frame_num = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        ret, frame = self.cap.read()
        # Convert the image to HLS
        frame_hls = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)
        # Calculate the mean color of every key
        means = {piano_key : cv2.mean(frame_hls, mask=self.masks[piano_key]) for piano_key in range(len(self.config.key_contours))}
        # Obtain which keys are pressed by which hand
        pressed_keys = set(self.matches_reference_key_color(key, mean) for key, mean in means.items() if self.matches_reference_key_color(key, mean) is not None)

        # Update the state and transmit the midi events
        self.update_state(pressed_keys, frame_num)
        
        # and all the masks of the found keys
        if self.generate_masks:
            base = np.zeros(frame.shape[:2], np.uint8)
            merged_mask = functools.reduce(cv2.bitwise_or, [self.masks[key] for key, hand in pressed_keys], base)
            merged_mask_inv = cv2.bitwise_not(merged_mask)

            red_bg = np.zeros(frame.shape, np.uint8)
            red_bg[:] = (0, 0, 255)
            red_bg = cv2.bitwise_and(red_bg, red_bg, mask=merged_mask)
            frame = cv2.bitwise_and(frame, frame, mask=merged_mask_inv)
            # invert that mask and apply it to background (frame)
            frame = cv2.bitwise_or(frame, red_bg)
        return frame