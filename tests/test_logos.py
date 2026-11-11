import io
import urllib.error

import pytest
from PIL import Image

from statsbombplot import plotting
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


class _Response(io.BytesIO):
    """Stands in for the object urlopen returns (a context manager that can be read)."""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _png_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), "red").save(buffer, format="PNG")
    return buffer.getvalue()


def test_logo_is_downloaded_with_a_timeout(monkeypatch):
    seen = {}

    def fake_urlopen(url, timeout=None):
        seen["timeout"] = timeout
        return _Response(_png_bytes())

    monkeypatch.setattr(plotting.urllib.request, "urlopen", fake_urlopen)
    img = load_team_logo("Arsenal")
    assert img.mode == "RGBA"
    assert seen["timeout"] == plotting.LOGO_TIMEOUT_SECONDS


@pytest.mark.parametrize("kind", ["http_403", "network", "timeout"])
def test_failed_download_falls_back_to_no_logo(monkeypatch, kind):
    errors = {
        "http_403": urllib.error.HTTPError("u", 403, "Forbidden", {}, io.BytesIO(b"")),
        "network": urllib.error.URLError("no route"),
        "timeout": TimeoutError("timed out"),
    }

    def fake_urlopen(url, timeout=None):
        raise errors[kind]

    monkeypatch.setattr(plotting.urllib.request, "urlopen", fake_urlopen)
    assert load_team_logo("Arsenal") is None


def test_unreadable_image_falls_back_to_no_logo(monkeypatch):
    monkeypatch.setattr(
        plotting.urllib.request, "urlopen", lambda url, timeout=None: _Response(b"not an image")
    )
    assert load_team_logo("Arsenal") is None
