import matplotlib.pyplot as plt
from common import config, draw_pitch, change_range, get_statsbomb_api
import matplotlib.lines as mlines


def draw_event_type_scatter(
    events,
    filename,
    event_type,
    draw_mean_height=True,
    marker_shape="o",
    marker_color=(0.765, 0.388, 0.961, 0.8),
):
    figsize_ratio = config["fig_size"] / 12
    ax = draw_pitch()

    shapes = []
    labels = []

    count_opponent_half = 0
    for i, event in events.iterrows():
        markersize = 50 * figsize_ratio
        linewidth = 0.5 * figsize_ratio
        fontsize = 6 * figsize_ratio

        # Statsbomb pitch dimensions: 120 length, 80 width

        x = change_range(event.location[0], [0, 120], [0, 105])
        y = change_range(event.location[1], [0, 80], [0, 68])

        if x > 52.5:
            count_opponent_half += 1

        ax.scatter(
            x,
            y,
            s=markersize,
            edgecolor="black",
            linewidth=linewidth,
            facecolor=marker_color,
            zorder=7,
            marker=marker_shape,
        )

    legend_elements = [
        plt.scatter(
            x,
            y,
            s=markersize,
            edgecolor="black",
            linewidth=linewidth,
            facecolor=marker_color,
            zorder=7,
            marker=marker_shape,
            label=event_type,
        )
    ]

    if draw_mean_height:
        events["X"] = events["location"].apply(lambda loc: loc[0])
        events["Y"] = events["location"].apply(lambda loc: loc[1])

        # Group by the 'event_id' and calculate the mean X and Y for each ball recovery
        mean_coordinates = events[["X", "Y"]].mean()
        avg_ball_recovery_x = change_range(mean_coordinates.X, [0, 120], [0, 105])

        ax.axvline(
            x=avg_ball_recovery_x,
            ymin=0.0625,
            ymax=0.9375,
            color=(0.88, 0.48, 0.37, 0.8),
            linewidth=2,
            zorder=4,
            linestyle="dashed",
        )

        legend_elements.extend(
            [
                mlines.Line2D(
                    [],
                    [],
                    color=(0.88, 0.48, 0.37, 0.8),
                    linewidth=2,
                    linestyle="dashed",
                    label=f"Mean Height of {event_type}",
                )
            ]
        )

    markersize = 50 * figsize_ratio
    linewidth = 0.5 * figsize_ratio

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

    percentage_opponent_half = round(100 * count_opponent_half / len(events), 2)
    ax.text(92.5, -2.1, "@francescozonaro", fontsize=10, va="center")
    ax.text(
        0, -2.1, f"Number of events: {len(events)}", fontsize=7, va="center", ha="left"
    )
    ax.text(
        0,
        -4.1,
        f"Percentage in opponent half: {percentage_opponent_half}%",
        fontsize=7,
        va="center",
        ha="left",
    )

    plt.savefig(f"imgs/{filename}.png", bbox_inches="tight", format="png", dpi=300)


api = get_statsbomb_api()

g = 3795506
df_teams = api.teams(game_id=g)
df_players = api.players(game_id=g)
df_events = api.events(game_id=g, load_360=True)
teams = list(df_events["team_name"].unique())
teams_id = list(df_events["team_id"].unique())
draw_id = 0

# Group the events to plot. Remember: Everything is plotted with the same marker. In this example we are plotting defensive actions.
types = [
    "Block",
    "Interception",
    "Clearance",
    "Ball Recovery",
]
df = df_events[df_events["type_name"].isin(types)]

# Decide the team to plot
df = df[df["team_id"] == teams_id[draw_id]].reset_index(drop=True)

# Sometimes it may be useful to ignore the keeper
df = df[df["position_name"] != "Goalkeeper"]

# We consider only situations where the opponent has the ball
df = df[df["possession_team_id"] == teams_id[abs(draw_id - 1)]]

draw_event_type_scatter(
    df,
    filename=f"defAction{teams[draw_id].split()[0]}",
    event_type=f"{teams[draw_id]} Def. Action",
    marker_shape="p",
    marker_color=(0.5, 0.78, 0.97, 1),
)
