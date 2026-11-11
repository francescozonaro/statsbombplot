from .full import FullPitch


class HalfPitch(FullPitch):
    """A pitch in StatsBomb coordinates (120 x 80) drawn showing only its right half."""

    def __init__(self):
        super().__init__()
        self.background_color = "white"
        self.x_start = 0.5
        self.circle_angles = (-90, 90)
