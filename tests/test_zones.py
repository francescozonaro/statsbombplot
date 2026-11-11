import numpy as np

from statsbombplot.pitch import count_in_pitch_zones


def test_counts_land_in_the_right_zone():
    x = np.array([5.0, 5.0, 115.0])
    y = np.array([5.0, 5.0, 75.0])
    counts = count_in_pitch_zones(x, y, zones_x=6, zones_y=4)
    assert counts.shape == (4, 6)
    assert counts[0, 0] == 2
    assert counts[3, 5] == 1
    assert counts.sum() == 3


def test_points_outside_the_pitch_are_ignored():
    counts = count_in_pitch_zones(np.array([120.0]), np.array([80.0]), zones_x=6, zones_y=4)
    assert counts.sum() == 0
