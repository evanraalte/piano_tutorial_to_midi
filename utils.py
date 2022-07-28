from Noterator import Notes
import collections
import numpy as np


def find_start_note(notes) -> Notes:
    if len(notes) < len(Notes):
        raise Exception(f"Need at least {len(Notes)} notes to determine the start note")
    c_note = [n for n in "WBWBWWBWBWBW"]
    reference = collections.deque(c_note)
    for count in range(0, len(Notes)):
        if notes[0 : len(c_note)] == list(reference):
            return Notes(count)
        reference.rotate(-1)
    raise Exception("Start note not found")


def get_median_filtered_mask(signal, threshold=30):
    signal = np.array(signal)
    difference = np.abs(signal - np.median(signal))
    median_difference = np.median(difference)

    if median_difference == 0:
        s = 0
    else:
        s = difference / float(median_difference)

    ret = s < threshold
    return [ret] if type(ret) is bool else ret
