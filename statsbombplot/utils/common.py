import warnings
from statsbombpy.api_client import NoAuthWarning
from .loader import Loader

warnings.simplefilter("ignore", NoAuthWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


def changeRange(value, oldRange, newRange):
    """
    Convert a value from one range to another one, maintaining ratio.
    """
    return ((value - oldRange[0]) / (oldRange[1] - oldRange[0])) * (
        newRange[1] - newRange[0]
    ) + newRange[0]


def getStatsbombAPI():
    api = Loader(creds={"user": "", "passwd": ""})
    return api


def adjustColor(color_hex, offset):
    """Adjust the color hex by a given offset."""
    r = int(color_hex[1:3], 16)
    g = int(color_hex[3:5], 16)
    b = int(color_hex[5:7], 16)
    r = min(max(r + offset, 0), 255)
    g = min(max(g + offset, 0), 255)
    b = min(max(b + offset, 0), 255)
    return f"#{r:02x}{g:02x}{b:02x}"


def deriveNearColors(color_hex):
    """Derive two colors near the given color."""

    offset1 = 60  # Modify as needed
    offset2 = -60  # Modify as needed
    color1 = adjustColor(color_hex, offset1)
    color2 = adjustColor(color_hex, offset2)

    return [color1, color2]


def addNotes(ax, author, extra_text=None):
    """
    Adds author tag and extra text to the bottom left of the plot.
    """
    ax.text(92.5, -2.1, author, fontsize=10, va="center")

    if extra_text:
        for i, text in enumerate(extra_text):
            ax.text(
                0,
                -2.1 - 2 * i,
                text,
                fontsize=7,
                va="center",
                ha="left",
            )


def addLegend(ax, legendElements):
    """
    Adds legend at the top of the plot
    """
    ax.legend(
        handles=legendElements,
        loc="upper center",
        ncol=len(legendElements),
        bbox_to_anchor=(0.5, 0.99),
        fontsize=10,
        fancybox=True,
        frameon=True,
        handletextpad=0.5,
    )


def saveFigure(fig, filename, dpi=300):
    """
    Saves the figure to a file with the given dpi.
    """
    fig.savefig(filename, bbox_inches="tight", format="png", dpi=dpi)
