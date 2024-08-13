import warnings
from statsbombpy.api_client import NoAuthWarning
from .loader import Loader

warnings.simplefilter("ignore", NoAuthWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

config = {
    "background_color": "white",
    "lines_color": "#bcbcbc",
    "edges_cmap": "Oranges",
    "nodes_cmap": "Reds",
    "font_color": "black",
    "plot_edges": True,
    "fig_size": 15,
    "font_size": 9,
    "width": 105,
    "height": 68,
    "max_node_size": 100,
    "min_node_size": 25,
    "max_edge_width": 5,
    "min_edge_width": 1,
}


def change_range(value, old_range, new_range):
    """
    Convert a value from one range to another one, maintaining ratio.
    """
    return ((value - old_range[0]) / (old_range[1] - old_range[0])) * (
        new_range[1] - new_range[0]
    ) + new_range[0]


def get_statsbomb_api():
    api = Loader(creds={"user": "", "passwd": ""})
    return api
