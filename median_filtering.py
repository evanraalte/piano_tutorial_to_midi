import numpy as np

data = [
    2726,
    223,
    3754,
    3834,
    223,
    3835,
    3747,
    3819,
    223,
    3828,
    3760,
    223,
    3742,
    3822,
    3733,
    223,
    3723,
    3865,
    223,
    3854,
    3757,
    3852,
    223,
    3802,
    3753,
    223,
    3754,
    3846,
    3768,
]


def get_median_filtered(old_signal, threshold=30):
    signal = np.array(old_signal)
    difference = np.abs(signal - np.median(signal))
    median_difference = np.median(difference)

    if median_difference == 0:
        s = 0
    else:
        s = difference / float(median_difference)

    mask = s < threshold
    return signal[mask]


x = get_median_filtered(data)
print(x)
