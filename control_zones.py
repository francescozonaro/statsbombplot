import matplotlib.pyplot as plt
from statsbombplot.utils import config, draw_pitch, change_range
import numpy as np
import matplotlib.patches as patches


def interpolate_color(initial, final, num_colors):
    # Convert hexadecimal color strings to RGB tuples
    initial_rgb = tuple(int(initial[i : i + 2], 16) for i in (1, 3, 5))
    final_rgb = tuple(int(final[i : i + 2], 16) for i in (1, 3, 5))

    # Calculate the step size for each RGB component
    r_step = (final_rgb[0] - initial_rgb[0]) / (num_colors - 1)
    g_step = (final_rgb[1] - initial_rgb[1]) / (num_colors - 1)
    b_step = (final_rgb[2] - initial_rgb[2]) / (num_colors - 1)

    # Generate the color map
    color_map = []
    for i in range(num_colors):
        r = int(initial_rgb[0] + i * r_step)
        g = int(initial_rgb[1] + i * g_step)
        b = int(initial_rgb[2] + i * b_step)
        color_map.append("#{:02X}{:02X}{:02X}".format(r, g, b))

    return color_map


def draw_control_zones(events, filename, pov_id):
    figsize_ratio = config["fig_size"] / 12
    ax = draw_pitch()

    num_rows = 6
    num_columns = 8
    width = 105
    height = 68

    row_step = 68 / num_rows
    column_step = width / num_columns

    grid = np.zeros((num_rows, num_columns))

    cell_colors = interpolate_color("#BF616A", "#5E81AC", 5)

    # Plot vertical grid lines
    for i in range(num_columns - 1):
        x = (i + 1) * column_step
        ax.plot([x, x], [0, height], "--", color="black", alpha=0.4, lw=1, zorder=9)

    # Plot horizontal grid lines
    for i in range(num_rows - 1):
        y = (i + 1) * row_step
        ax.plot(
            [0, width],
            [y, y],
            "--",
            color="black",
            alpha=0.4,
            lw=1,
            zorder=9,
        )

    teams = []
    teams_name = []

    for i, event in events.iterrows():
        markersize = 50 * figsize_ratio
        linewidth = 0.5 * figsize_ratio
        fontsize = 6 * figsize_ratio

        if event.team_id == pov_id:
            x = change_range(event.location[0], [0, 120], [0, 105])
            y = 68 - change_range(event.location[1], [0, 80], [0, 68])
            weight = +1
        else:
            x = 105 - change_range(event.location[0], [0, 120], [0, 105])
            y = change_range(event.location[1], [0, 80], [0, 68])
            weight = -1

        x_idx = int(x // column_step)
        x_idx = min(x_idx, num_columns - 1)
        y_idx = int(y // row_step)
        y_idx = min(y_idx, num_rows - 1)
        grid[y_idx, x_idx] += weight

    for y_idx in range(num_rows):
        for x_idx in range(num_columns):
            cell_count = grid[y_idx, x_idx]

            if cell_count > 20:
                cell_color = cell_colors[4]
            elif cell_count < -20:
                cell_color = cell_colors[0]
            else:
                cell_color = "#D8DEE9"

            cell_rect = patches.Rectangle(
                (x_idx * column_step, y_idx * row_step),
                column_step,
                row_step,
                edgecolor=(1, 1, 1, 0),
                facecolor=cell_color,
            )
            ax.add_patch(cell_rect)

    ax.text(92.5, -2.1, "@francescozonaro", fontsize=10, va="center")

    plt.savefig(f"{filename}.png", bbox_inches="tight", format="png", dpi=300)
