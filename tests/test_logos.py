from statsbombplot.config import FOTMOB_URL, TEAM_LOGO_URL
from statsbombplot.plotting import load_team_logo


def test_logo_table_covers_clubs_and_national_teams():
    assert TEAM_LOGO_URL["Arsenal"] == f"{FOTMOB_URL}9825.png"
    assert TEAM_LOGO_URL["Italy"].startswith(FOTMOB_URL)
    assert "Arsenal WFC" in TEAM_LOGO_URL  # women's teams are separate entries


def test_all_logo_urls_are_wellformed():
    assert len(TEAM_LOGO_URL) > 300
    for url in TEAM_LOGO_URL.values():
        assert url.startswith(FOTMOB_URL) and url.endswith(".png")


def test_unknown_team_has_no_logo():
    assert load_team_logo("Definitely Not A Team") is None
