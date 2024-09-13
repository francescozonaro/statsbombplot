import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


class Pitch:
    def __init__(self):
        self.height = float(68)
        self.width = float(105)
        self.background_color = "white"
        self.lines_color = "#bcbcbc"
        self.fig_size = 15

    def _point_to_meters(self, p):
        """Convert a point's coordinates from a 0-1 range to meters."""
        return np.array([p[0] * self.width, p[1] * self.height])

    def _meters_to_point(self, p):
        """Convert a point's coordinates from meters to a 0-1 range."""
        return np.array([p[0] / self.width, p[1] / self.height])

    def _draw_pitch_elements(self, ax, lines_color):
        line_pts = [
            [
                self._point_to_meters([0.5, 0]),
                self._point_to_meters([0.5, 1]),
            ],  # center line
            # left box
            [[0, 13.85], [16.5, 13.85]],
            [[0, 54.15], [16.5, 54.15]],
            [[16.5, 13.85], [16.5, 54.15]],
            # left goal
            [[0, 24.85], [5.5, 24.85]],
            [[0, 43.15], [5.5, 43.15]],
            [[5.5, 24.85], [5.5, 43.15]],
            [[0.0, 29.85], [0.0, 38.15]],
            [[0.1, 29.85], [0.1, 38.15]],
            # right box
            [[105, 13.85], [88.5, 13.85]],
            [[105, 54.15], [88.5, 54.15]],
            [[88.5, 13.85], [88.5, 54.15]],
            # right goal
            [[105, 24.85], [99.5, 24.85]],
            [[105, 43.15], [99.5, 43.15]],
            [[99.5, 24.85], [99.5, 43.14]],
            [[104.9, 29.85], [104.9, 38.15]],
            [[105, 29.85], [105, 38.15]],
        ]

        for line_pt in line_pts:
            ax.plot(
                [line_pt[0][0], line_pt[1][0]],
                [line_pt[0][1], line_pt[1][1]],
                "-",
                alpha=0.8,
                lw=1.5,
                zorder=3,
                color=lines_color,
            )

        ax.add_patch(
            patches.Wedge(
                (94.0, 34.0),
                9,
                130,
                230,
                fill=True,
                edgecolor=lines_color,
                facecolor=lines_color,
                zorder=4,
                width=0.02,
                alpha=0.8,
            )
        )

        ax.add_patch(
            patches.Wedge(
                (11.0, 34.0),
                9,
                310,
                50,
                fill=True,
                edgecolor=lines_color,
                facecolor=lines_color,
                zorder=4,
                width=0.02,
                alpha=0.8,
            )
        )

        ax.add_patch(
            patches.Wedge(
                (52.5, 34),
                9.5,
                0,
                360,
                fill=True,
                edgecolor=lines_color,
                facecolor=lines_color,
                zorder=4,
                width=0.02,
                alpha=0.8,
            )
        )

    def draw(self):
        """
        Plot an empty horizontal football pitch, returning Matplotlib's ax object so we can keep adding elements to it.
        """

        ratio = self.height / float(self.width)
        f, ax = plt.subplots(
            1, 1, figsize=(self.fig_size, self.fig_size * ratio), dpi=600
        )
        ax.set_ylim([-5, self.height + 5])
        ax.set_xlim([-5, self.width + 5])
        ax.add_patch(
            patches.Rectangle(
                (0, 0), self.width, self.height, color=self.background_color
            )
        )

        # Plot outer lines
        line_pts = [
            [self._point_to_meters([0, 0]), self._point_to_meters([0, 1])],  # left line
            [
                self._point_to_meters([1, 0]),
                self._point_to_meters([1, 1]),
            ],  # right line
            [self._point_to_meters([0, 1]), self._point_to_meters([1, 1])],  # top line
            [
                self._point_to_meters([0, 0]),
                self._point_to_meters([1, 0]),
            ],  # bottom line
        ]

        for line_pt in line_pts:
            ax.plot(
                [line_pt[0][0], line_pt[1][0]],
                [line_pt[0][1], line_pt[1][1]],
                "-",
                alpha=0.8,
                lw=1.5,
                zorder=3,
                color=self.lines_color,
            )

        self._draw_pitch_elements(ax, self.lines_color)

        plt.axis("off")
        return f, ax
