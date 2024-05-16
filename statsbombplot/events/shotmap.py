import matplotlib.pyplot as plt
from statsbombplot.utils import config, draw_pitch, change_range


def draw_shotmap(
    events,
    filename,
    team_left_id,
    left_color=(0.5, 0.78, 0.97, 1),
    right_color=(0.88, 0.48, 0.37, 1),
):

    figsize_ratio = config["fig_size"] / 12
    ax = draw_pitch()

    teams = []
    teams_name = []

    for i, event in events.iterrows():

        markersize = 50 * figsize_ratio
        linewidth = 0.5 * figsize_ratio
        fontsize = 6 * figsize_ratio
        shot_xG = round(event.extra["shot"]["statsbomb_xg"], 3)
        multiplier_xG = round(change_range(shot_xG, [0, 1], [1, 5]), 3)
        markersize = markersize * multiplier_xG

        shot_technique = event.extra["shot"]["technique"]["name"]

        if shot_technique == "Normal":
            shot_technique = event.extra["shot"]["body_part"]["name"]

        teams.append(event.team_id)
        teams_name.append(event.team_name)

        # Statsbomb pitch dimensions: 120 length, 80 width
        if event.team_id != team_left_id:
            x = change_range(event.location[0], [0, 120], [0, 105])
            y = 68 - change_range(event.location[1], [0, 80], [0, 68])
            shot_color = right_color
        else:
            x = 105 - change_range(event.location[0], [0, 120], [0, 105])
            y = change_range(event.location[1], [0, 80], [0, 68])
            shot_color = left_color

        if event.extra["shot"]["outcome"]["name"] == "Goal":
            ax.scatter(
                x,
                y,
                s=markersize * 1.5,
                edgecolor="black",
                linewidth=linewidth,
                facecolor=shot_color,
                zorder=7,
                marker="*",
            )
        elif event.extra["shot"]["outcome"]["name"] == "Saved":
            ax.scatter(
                x,
                y,
                s=markersize,
                edgecolor="black",
                linewidth=linewidth,
                facecolor=shot_color,
                zorder=6,
                marker="o",
            )
        else:
            ax.scatter(
                x,
                y,
                s=markersize,
                edgecolor="black",
                linewidth=linewidth,
                facecolor=shot_color,
                zorder=5,
                marker="X",
            )

    markersize = 50 * figsize_ratio
    linewidth = 0.5 * figsize_ratio

    legend_elements = [
        plt.scatter(
            [],
            [],
            s=markersize * 1.2,
            edgecolor="black",
            linewidth=linewidth,
            facecolor=(1, 1, 1, 0.8),
            zorder=5,
            marker="*",
            label="Goal",
        ),
        plt.scatter(
            [],
            [],
            s=markersize,
            edgecolor="black",
            linewidth=linewidth,
            facecolor=(1, 1, 1, 0.8),
            zorder=5,
            marker="o",
            label="On Target",
        ),
        plt.scatter(
            [],
            [],
            s=markersize,
            edgecolor="black",
            linewidth=linewidth,
            facecolor=(1, 1, 1, 0.8),
            zorder=5,
            marker="X",
            label="Off Target",
        ),
        plt.scatter(
            [],
            [],
            s=markersize / 3,
            edgecolor="black",
            linewidth=linewidth,
            facecolor=(1, 1, 1, 0.8),
            zorder=5,
            marker="o",
            label="Low xG",
        ),
        plt.scatter(
            [],
            [],
            s=markersize * 2,
            edgecolor="black",
            linewidth=linewidth,
            facecolor=(1, 1, 1, 0.8),
            zorder=5,
            marker="o",
            label="High xG",
        ),
    ]

    ax.legend(
        handles=legend_elements,
        loc="upper center",
        ncol=len(legend_elements),
        bbox_to_anchor=(0.5, 0.99),
        fontsize=10,
        fancybox=True,
        frameon=True,
        handletextpad=0.5,
    )

    ax.text(92.5, -2.1, "@francescozonaro", fontsize=10, va="center")

    for team, name in zip(teams, teams_name):
        if team == team_left_id:
            ax.text(1, 66, f"{name}", fontsize=10, va="center", ha="left")
        else:
            ax.text(104, 66, f"{name}", fontsize=10, va="center", ha="right")

    plt.savefig(f"imgs/{filename}.png", bbox_inches="tight", format="png", dpi=300)
