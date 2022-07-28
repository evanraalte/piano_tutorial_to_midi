from dataclasses import dataclass
from enum import Enum
from itertools import cycle


class Notes(Enum):
    C = 0
    Db = 1
    D = 2
    Eb = 3
    E = 4
    F = 5
    Gb = 6
    G = 7
    Ab = 8
    A = 9
    Bb = 10
    B = 11


@dataclass
class Note:
    MIDI_OFFSET = 45
    octave: int
    note: Notes

    @property
    def midi_num(self):
        return self.note.value + self.octave * 12 + self.MIDI_OFFSET

    def __str__(self):
        return f"{self.note.name}{self.octave}"


class Noterator:
    MIDI_OFFSET = 45
    START_NOTE = Notes.C
    START_OCTAVE = -2
    END_OCTAVE = 8

    def __init__(self, cyclic=False):
        cycle_function = cycle if cyclic else iter

        self.iterator_note = cycle(Notes)
        self.iterator_octave = cycle_function(range(self.START_OCTAVE, self.END_OCTAVE + 1))
        self.note = next(self.iterator_note)
        self.octave = next(self.iterator_octave)

    def __iter__(self):
        return self

    def __next__(self):
        ret = Note(note=self.note, octave=self.octave)

        self.note = next(self.iterator_note)
        if self.note == self.START_NOTE:  # Changed back to Start note
            self.octave = next(self.iterator_octave)  # Iterate over octave
        return ret


# print(Notes[0])
# print([str(x) for x in Noterator() if x.note == Notes.C])
