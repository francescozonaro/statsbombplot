import pickle

import pandas as pd
import pytest

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


def _use_fake_api(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(fetch, "get_statsbomb_api", FakeApi)
    FakeApi.calls = 0


def test_truncated_cache_file_is_downloaded_again(tmp_path, monkeypatch):
    _use_fake_api(monkeypatch, tmp_path)
    fetch._get_cache_path(1).write_bytes(pickle.dumps({"x": 1})[:5])  # an interrupted write

    match = fetch.fetch_match(1)

    assert match.home_team_name == "A" and FakeApi.calls == 1
    assert fetch.fetch_match(1).home_team_name == "A" and FakeApi.calls == 1  # repaired


def test_failed_write_leaves_no_cache_or_temp_file(tmp_path, monkeypatch):
    _use_fake_api(monkeypatch, tmp_path)

    def broken_dump(obj, file):
        file.write(b"partial")
        raise KeyboardInterrupt

    monkeypatch.setattr(fetch.pickle, "dump", broken_dump)
    with pytest.raises(KeyboardInterrupt):
        fetch.fetch_match(1)

    assert list(tmp_path.iterdir()) == []


def test_prefetch_downloads_each_uncached_game_once(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch, "CACHE_DIR", tmp_path)
    fetch._get_cache_path(2).write_bytes(b"already cached")
    seen = []
    monkeypatch.setattr(fetch, "_warm", seen.append)

    fetch.prefetch_matches([3, 1, 3, 2, 1], workers=1)

    assert sorted(seen) == [1, 3]  # no duplicates, and game 2 is skipped
