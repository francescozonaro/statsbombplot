from __future__ import annotations

import math
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from PIL import Image

from .config import FONT_FAMILY, TEAM_LOGO_URL


def apply_style() -> None:
    """Apply the default matplotlib style (font family) used by all plots."""
    plt.rcParams["font.family"] = FONT_FAMILY


LOGO_TIMEOUT_SECONDS = 10


def load_team_logo(team: str, mode: str = "RGBA") -> Image.Image | None:
    """Download a team's logo, or return None if we have none or the download fails."""
    url = TEAM_LOGO_URL.get(team)
    if url is None:
        return None
    try:
        with urllib.request.urlopen(url, timeout=LOGO_TIMEOUT_SECONDS) as response:
            return Image.open(response).convert(mode)
    except OSError:  # timeout, HTTP/network error or an unreadable image
        return None


def save_figure(fig: Figure, path: str | Path, dpi: int = 300) -> None:
    """Save the figure as a PNG at `path`, creating parent folders if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", format="png", dpi=dpi)


def make_matplotlib_grid(
    n_items: int, max_cols: int = 5, subplot_width: float = 4, ratio: float = 80 / 120
) -> tuple[Figure, np.ndarray]:
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
