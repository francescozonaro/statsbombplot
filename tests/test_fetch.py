import pandas as pd

from statsbombplot.data import fetch


class FakeApi:
    calls = 0

    def events(self, game_id, load_360=False):
        FakeApi.calls += 1
        return pd.DataFrame({"type_name": ["Shot"]})

    def players(self, game_id):
        return pd.DataFrame()

    def teams(self, game_id):
        return pd.DataFrame({"team_id": [1, 2], "team_name": ["A", "B"]})


def test_fetch_match_downloads_once_then_uses_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(fetch, "get_statsbomb_api", FakeApi)
    FakeApi.calls = 0

    first = fetch.fetch_match(1)
    second = fetch.fetch_match(1)

    assert FakeApi.calls == 1
    assert second.home_team_name == first.home_team_name == "A"
    assert len(list(tmp_path.glob("*.pkl"))) == 1


def test_teams_include_sides_that_only_played_away(monkeypatch):
    games = pd.DataFrame(
        {"home_team_name": ["Barcelona", "Barcelona"], "away_team_name": ["Huesca", "Celta Vigo"]}
    )
    monkeypatch.setattr(fetch, "get_games", lambda competition_id, season_id: games)
    assert fetch.get_teams_by_season(11, 4) == ["Barcelona", "Celta Vigo", "Huesca"]
