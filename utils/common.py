import warnings
from statsbombpy.api_client import NoAuthWarning
from .loader import Loader

warnings.simplefilter("ignore", NoAuthWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


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


def adjust_color(color_hex, offset):
    """Adjust the color hex by a given offset."""
    r = int(color_hex[1:3], 16)
    g = int(color_hex[3:5], 16)
    b = int(color_hex[5:7], 16)
    r = min(max(r + offset, 0), 255)
    g = min(max(g + offset, 0), 255)
    b = min(max(b + offset, 0), 255)
    return f"#{r:02x}{g:02x}{b:02x}"


def derive_near_colors(color_hex):
    """Derive two colors near the given color."""

    offset1 = 60  # Modify as needed
    offset2 = -60  # Modify as needed
    color1 = adjust_color(color_hex, offset1)
    color2 = adjust_color(color_hex, offset2)

    return [color1, color2]
