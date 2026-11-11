import pandas as pd

from statsbombplot.data import Match


def make_match():
    teams = pd.DataFrame({"team_id": [1, 2], "team_name": ["Italy", "England"]})
    return Match(42, pd.DataFrame(), teams, pd.DataFrame())


def test_home_team_is_first_row():
    match = make_match()
    assert (match.home_team_name, match.home_team_id) == ("Italy", 1)
    assert (match.away_team_name, match.away_team_id) == ("England", 2)


def test_team_lists_keep_home_first():
    match = make_match()
    assert match.team_names == ["Italy", "England"]
    assert match.team_ids == [1, 2]
