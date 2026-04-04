"""
ride quality analysis from phone sensors.
bumpiness from accelerometer, lean from orientation, braking from GPS speed.
"""

import numpy as np


def compute_bumpiness(pos, acc):
    """
    for each GPS second, get the accelerometer vibration intensity.
    = RMS of (acc_magnitude - gravity). higher = rougher road.
    """
    timestamps = pos['timestamp'].values
    acc_ts = acc['timestamp'].values
    acc_ax = acc['ax'].values
    acc_ay = acc['ay'].values
    acc_az = acc['az'].values

    bumpiness = np.zeros(len(timestamps))

    for i in range(1, len(timestamps)):
        a0 = np.searchsorted(acc_ts, timestamps[i - 1])
        a1 = np.searchsorted(acc_ts, timestamps[i])

        if a1 - a0 < 3:
            bumpiness[i] = bumpiness[i - 1]
            continue

        mag = np.sqrt(acc_ax[a0:a1]**2 + acc_ay[a0:a1]**2 + acc_az[a0:a1]**2)
        dynamic = mag - 9.81
        bumpiness[i] = np.sqrt(np.mean(dynamic**2))

    return bumpiness


def compute_lean(pos, orient):
    """average absolute roll angle per GPS interval. roll = bike leaning."""
    timestamps = pos['timestamp'].values
    orient_ts = orient['timestamp'].values
    orient_roll = orient['roll'].values

    lean = np.zeros(len(timestamps))

    for i in range(1, len(timestamps)):
        o0 = np.searchsorted(orient_ts, timestamps[i - 1])
        o1 = np.searchsorted(orient_ts, timestamps[i])

        if o1 - o0 < 1:
            lean[i] = lean[i - 1]
            continue

        lean[i] = np.mean(np.abs(orient_roll[o0:o1]))

    return lean


def compute_braking(pos):
    """
    speed change between GPS fixes.
    negative = slowing down, positive = speeding up.
    """
    speed = pos['speed'].values
    braking = np.zeros(len(speed))
    for i in range(1, len(speed)):
        braking[i] = speed[i] - speed[i - 1]
    return braking


def find_rough_segments(bumpiness, threshold_pct=85):
    """find stretches where bumpiness is above the given percentile."""
    threshold = np.percentile(bumpiness[bumpiness > 0], threshold_pct)
    rough = bumpiness > threshold

    segments = []
    start = None
    for i in range(len(rough)):
        if rough[i] and start is None:
            start = i
        elif not rough[i] and start is not None:
            if i - start >= 3:
                segments.append((start, i))
            start = None
    if start is not None and len(rough) - start >= 3:
        segments.append((start, len(rough)))

    return segments, threshold
