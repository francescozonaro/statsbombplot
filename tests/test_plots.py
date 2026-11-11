import subprocess
import sys
from pathlib import Path

import pytest

PLOTS = sorted((Path(__file__).parent.parent / "plots").glob("*.py"))


@pytest.mark.parametrize("script", PLOTS, ids=lambda p: p.stem)
def test_plot_script_loads_and_shows_its_flags(script):
    """Importing the script and parsing its flags needs no network, so typos are caught here."""
    result = subprocess.run(
        [sys.executable, str(script), "--help"], capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stderr
    assert "usage:" in result.stdout


def test_every_plot_script_is_covered():
    assert PLOTS  # the glob found the scripts; adding a plot must not break this
