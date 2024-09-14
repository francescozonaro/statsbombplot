import warnings
from statsbombpy.api_client import NoAuthWarning
from .loader import Loader

warnings.simplefilter("ignore", NoAuthWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


def getStatsbombAPI():
    api = Loader(creds={"user": "", "passwd": ""})
    return api


def addNotes(ax, author, extra_text=None):
    """
    Adds author tag and extra text to the bottom left of the plot.
    """
    ax.text(105.8, -2.1, author, fontsize=10, va="center")

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
        bbox_to_anchor=(0.5, 1),
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
