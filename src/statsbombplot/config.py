import json
from pathlib import Path

# Paths (relative to the working directory)
OUTPUT_DIR = Path("output")
CACHE_DIR = Path("match_cache")

# Pitch dimensions (StatsBomb)
PITCH_WIDTH = 120
PITCH_HEIGHT = 80
PITCH_RATIO = PITCH_HEIGHT / PITCH_WIDTH

# Typography
FONT_FAMILY = "Monospace"

# Branding
PERSONAL_WATERMARK = "@francescozonaro"

# Colors
FIG_BACKGROUND_COLOR = "#f9f7f3"
PURPLE_HEX = "#7956a4"
GRAY_HEX = "#535353"
LIGHT_GRAY_HEX = "#707070"
PLAIN_WHITE_HEX = "#ffffff"
PLAIN_BLACK_HEX = "#000000"

# Team logos: StatsBomb team name -> Fotmob team id (see team_logos.json)
FOTMOB_URL = "https://images.fotmob.com/image_resources/logo/teamlogo/"
TEAM_LOGO_URL = {
    name: f"{FOTMOB_URL}{fotmob_id}.png"
    for name, fotmob_id in json.loads(
        (Path(__file__).parent / "team_logos.json").read_text(encoding="utf-8")
    ).items()
}
