import numpy as np

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
