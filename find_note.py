# Nice for future reference :)
from collections import deque

reference = deque(c for c in "WBWBWWBWBWBW")


for slice_size in range(0, 12):
    start_set = set()
    for _ in range(0, 12):  # go over all keys
        start = "".join(list(reference)[0:slice_size])
        start_set.add(start)
        print(start)
        reference.rotate(1)
    if len(start_set) == 12:
        print(f"Deducable with {slice_size} keys")
        break
    else:
        print(f"Set has size of {len(start_set)}")


# WBWBWWBWBW
# WWBWBWWBWB
# BWWBWBWWBW
# WBWWBWBWWB
# BWBWWBWBWW
# WBWBWWBWBW
# BWBWBWWBWB
# WBWBWBWWBW
# WWBWBWBWWB
# BWWBWBWBWW
# WBWWBWBWBW
# BWBWWBWBWB
