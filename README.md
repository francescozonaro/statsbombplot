# statsbombplot

Football analytics visualizations built on [StatsBomb open data](https://github.com/statsbomb/open-data).
Shot maps, passing networks, goalkeeper distribution, shot freeze frames and more, drawn with matplotlib on
a StatsBomb-coordinate pitch.

## Installation

Requires Python 3.9+.

```bash
git clone https://github.com/francescozonaro/statsbombplot.git
cd statsbombplot
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

Every plot is a standalone script in [`examples/`](examples). Run one from the repository root:

```bash
python examples/shot_map.py                       # asks which match to plot
python examples/shot_map.py --game-id 3795506     # no questions
python examples/shooting_zones.py --competition-id 2 --season-id 27
```

Whatever a script needs and you did not pass, it asks for, listing only what exists in the open data:
competition, then its seasons, then (for match scripts) its games with date, gameweek or stage, and score.
At any prompt, type a number to pick, or type text (a team, a year) to filter the list.
Run a script with `--help` to see its flags. Without a terminal (e.g. in CI) all flags are required.

Images are written to `output/<script_name>/`. Match data is downloaded once from the StatsBomb open data
and cached in `match_cache/`.

| Script | What it draws |
| --- | --- |
| `shot_map.py` | Both teams' shots in a match, sized and shaded by xG |
| `shot_freeze_frame.py` | Player positions at the moment of a shot (360 data) |
| `shooting_zones.py` | Shot density per team over a season |
| `passing_networks.py` | Average positions and pass counts between players |
| `goalkeeper_pass_completion.py` | Long-pass share vs. completion rate for every team's goalkeeper |
| `goalkeeper_zonal_pass_distribution.py` | Where each team's goalkeeper distributes the ball |
| `goals_worth_watching.py` | The goals with the lowest xG of a competition, ranked |

## Project layout

```
src/statsbombplot/
  config.py        paths, colors, pitch dimensions
  cli.py           command-line flags and interactive prompts
  plotting.py      shared matplotlib helpers (style, save, grids)
  data/            StatsBomb loader, match model and cached fetching
  pitch/           full/half pitch drawing and zone counting
examples/          runnable plot scripts
tests/             unit tests (no network needed)
```

## Development

```bash
pytest          # run the tests
ruff check .    # lint
ruff format .   # format
```

## Data attribution

Data provided by [StatsBomb](https://statsbomb.com). Open data is free to use under
[StatsBomb's user agreement](https://github.com/statsbomb/open-data/blob/master/doc/StatsBomb%20Open%20Data%20Licence.pdf);
please credit StatsBomb in anything you publish.

## License

MIT, see [LICENSE](LICENSE).
