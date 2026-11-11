import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from statsbombplot.plotting import make_matplotlib_grid, save_figure  # noqa: E402


def test_save_figure_creates_missing_folders(tmp_path):
    fig, _ = plt.subplots()
    target = tmp_path / "a" / "b" / "fig.png"
    save_figure(fig, target, dpi=50)
    assert target.is_file()
    plt.close(fig)


def test_grid_hides_unused_axes():
    fig, axes = make_matplotlib_grid(n_items=3, max_cols=2)
    assert len(axes) == 4
    assert [ax.axison for ax in axes] == [True, True, True, False]
    plt.close(fig)
