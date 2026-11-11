import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .config import FONT_FAMILY


def apply_style():
    """Apply the default matplotlib style (font family) used by all plots."""
    plt.rcParams["font.family"] = FONT_FAMILY


def save_figure(fig, path, dpi=300):
    """Save the figure as a PNG at `path`, creating parent folders if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", format="png", dpi=dpi)


def make_matplotlib_grid(n_items, max_cols=5, subplot_width=4, ratio=80 / 120):
    """
    Create a grid of matplotlib subplots, hiding any unused axes.

    Parameters
    ----------
    n_items : int
        Number of subplots that will actually be used.
    max_cols : int, optional
        Maximum number of columns. Default is 5.
    subplot_width : float, optional
        Width of each subplot in inches. Default is 4.
    ratio : float, optional
        Height-to-width ratio of each subplot. Default is 80/120
        (StatsBomb pitch proportions).

    Returns
    -------
    fig : matplotlib.figure.Figure
    axes : np.ndarray
        Flattened array of Axes. First n_items are active,
        the rest are hidden.
    """
    n_cols = min(n_items, max_cols)
    n_rows = math.ceil(n_items / n_cols)
    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=(subplot_width * n_cols, subplot_width * n_rows * ratio)
    )
    axes = np.atleast_1d(axes).flatten()
    for i in range(n_items, len(axes)):
        axes[i].axis("off")
    return fig, axes
