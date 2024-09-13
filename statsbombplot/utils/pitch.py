import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


class Pitch:
    def __init__(self):
        self.height = float(80)  # Updated height
        self.width = float(120)  # Updated width
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
            # Center line
            [self._point_to_meters([0.5, 0]), self._point_to_meters([0.5, 1])],
            # Left penalty box
            [[0, 18], [17, 18]],  # Bottom line
            [[0, 62], [17, 62]],  # Top line
            [[17, 18], [17, 62]],  # Side line
            # Left goal area
            [[0, 31.5], [6, 31.5]],  # Bottom line
            [[0, 49.5], [6, 49.5]],  # Top line
            [[6, 31.5], [6, 49.5]],  # Side line
            [[-0.1, 36], [-0.1, 44]],  # Goal posts (left goal)
            [[0.0, 36], [0.0, 44]],  # Goal posts (left goal)
            [[0.1, 36], [0.1, 44]],
            [[0.2, 36], [0.2, 44]],
            # Right penalty box
            [[120, 18], [103, 18]],  # Bottom line
            [[120, 62], [103, 62]],  # Top line
            [[103, 18], [103, 62]],  # Side line
            # Right goal area
            [[120, 31.5], [114, 31.5]],  # Bottom line
            [[120, 49.5], [114, 49.5]],  # Top line
            [[114, 31.5], [114, 49.5]],  # Side line
            [[119.8, 36], [119.8, 44]],
            [[119.9, 36], [119.9, 44]],  # Goal posts (right goal)
            [[120, 36], [120, 44]],
            [[120.1, 36], [120.1, 44]],
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

        # Left penalty arc
        ax.add_patch(
            patches.Wedge(
                (11.0, 40),  # Center of the arc
                10,  # Radius
                308,
                52,
                fill=True,
                edgecolor=lines_color,
                facecolor=lines_color,
                zorder=4,
                width=0.02,
                alpha=0.8,
            )
        )

        # Right penalty arc
        ax.add_patch(
            patches.Wedge(
                (109.0, 40),  # Center of the arc
                10,  # Radius
                128,
                232,
                fill=True,
                edgecolor=lines_color,
                facecolor=lines_color,
                zorder=4,
                width=0.02,
                alpha=0.8,
            )
        )

        # Center circle
        ax.add_patch(
            patches.Wedge(
                (60, 40),  # Middle of the pitch
                10,  # Radius of the center circle
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
            [self._point_to_meters([0, 0]), self._point_to_meters([0, 1])],  # Left line
            [
                self._point_to_meters([1, 0]),
                self._point_to_meters([1, 1]),
            ],  # Right line
            [self._point_to_meters([0, 1]), self._point_to_meters([1, 1])],  # Top line
            [
                self._point_to_meters([0, 0]),
                self._point_to_meters([1, 0]),
            ],  # Bottom line
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
