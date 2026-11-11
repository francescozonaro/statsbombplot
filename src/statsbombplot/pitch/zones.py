import numpy as np


def count_in_pitch_zones(x, y, zones_x, zones_y, pitch_w=120, pitch_h=80):
    """
    Bin (x, y) coordinates into a grid and count occurrences per zone. Defaults to StatsBomb pitch dimensions (120x80) and orientation (y flipped).

    Parameters
    ----------
    x : np.ndarray
        Array of x coordinates.
    y : np.ndarray
        Array of y coordinates, already adjusted for orientation
        (e.g. 80 - raw_y for StatsBomb data).
    zones_x : int
        Number of horizontal zones to divide the pitch into.
    zones_y : int
        Number of vertical zones to divide the pitch into.
    pitch_w : float, optional
        Total pitch width in coordinate units. Default is 120 (StatsBomb).
    pitch_h : float, optional
        Total pitch height in coordinate units. Default is 80 (StatsBomb).

    Returns
    -------
    np.ndarray
        A (zones_y, zones_x) array where each cell contains the count of
        coordinates that fell within that zone. Coordinates outside the
        pitch boundaries are excluded.
    """
    rect_x, rect_y = pitch_w / zones_x, pitch_h / zones_y
    zx = (x // rect_x).astype(int)
    zy = (y // rect_y).astype(int)
    valid = (zx < zones_x) & (zy < zones_y)
    counts = np.zeros((zones_y, zones_x))
    np.add.at(counts, (zy[valid], zx[valid]), 1)
    return counts
