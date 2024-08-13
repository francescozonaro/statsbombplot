import socceraction.spadl as spadl
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from tabulate import tabulate

from common import config, draw_pitch, get_statsbomb_api


def nice_time(row):
    minute = int((row.period_id - 1) * 45 + row.time_seconds // 60)
    second = int(row.time_seconds % 60)
    return f"{minute}m{second}s"


def find_goal(df):
    df = df[
        ((df["type_id"] == 11) & (df["result_id"] == 1))
        | ((df["type_id"] == 12) & (df["result_id"] == 1) & (df["period_id"] < 5))
        | (df["result_id"] == 3)
    ]
    return df.index


def draw_match_goals(actions, with_labels=True):

    goals = list(find_goal(actions))

    for goal in goals:
        starting_id = goal
        df = actions[starting_id - 9 : starting_id + 1].copy()
        df = df.reset_index(drop=True)

        df["nice_time"] = df.apply(nice_time, axis=1)

        cols = ["nice_time", "player_name", "type_name", "result_name", "team_name"]

        print(tabulate(df[cols], headers=cols, showindex=True))
        draw_actions(df, "imgs/test_" + str(goal), with_labels)


def draw_actions(actions, filename, with_labels):

    figsize_ratio = config["fig_size"] / 12
    ax = draw_pitch()

    shapes = []
    labels = []

    for i, action in actions.iterrows():

        x = action["start_x"]
        x_end = action["end_x"]
        y = action["start_y"]
        y_end = action["end_y"]

        team_color = MAIN_COLOR if action["team_name"] == MAIN_TEAM else ALT_COLOR

        markersize = 0.8 * figsize_ratio
        linewidth = 1 * figsize_ratio
        fontsize = 6 * figsize_ratio

        if i >= 1:
            if (actions.iloc[i - 1].result_name == "success") & (
                action.type_name != "shot_penalty"
            ):
                x = actions.iloc[i - 1].end_x
                y = actions.iloc[i - 1].end_y

        # Symbol + Line

        if (action.type_name != "dribble") & (action.type_name != "foul"):

            if action.result_id == 3:
                action.type_name = "owngoal"

            shape = plt.Circle(
                (x, y),
                radius=markersize,
                edgecolor="black",
                linewidth=linewidth,
                facecolor=team_color,
                alpha=1,
                zorder=6,
            )
            shapes.append(shape)
            labels.append(
                action.type_name + "\n" + action.player_name + "\n" + action.team_name
            )

            if (
                action.type_name != "clearance"
                or actions.iloc[i + 1].type_name != "corner_crossed"
            ):
                line = patches.ConnectionPatch(
                    (x, y),
                    (x_end, y_end),
                    "data",
                    linestyle="-",
                    color="black",
                    linewidth=linewidth,
                    zorder=5,
                )
                shapes.append(line)
                labels.append(
                    action.type_name
                    + "\n"
                    + action.player_name
                    + "\n"
                    + action.team_name
                )

            if action.result_name == "fail" or action.result_name == "owngoal":
                shape = plt.Circle(
                    (x, y),
                    radius=markersize * 1.2,
                    edgecolor="red",
                    linewidth=linewidth,
                    facecolor=team_color,
                    alpha=0.3,
                    zorder=5,
                )
                shapes.append(shape)
                labels.append(
                    action.type_name
                    + "\n"
                    + action.player_name
                    + "\n"
                    + action.team_name
                )
                line = patches.ConnectionPatch(
                    (x, y),
                    (x_end, y_end),
                    "data",
                    linestyle="-",
                    color="red",
                    linewidth=linewidth * 2,
                    alpha=0.3,
                    zorder=5,
                )
                shapes.append(line)
                labels.append(
                    action.type_name
                    + "\n"
                    + action.player_name
                    + "\n"
                    + action.team_name
                )
        elif action.type_name == "dribble":
            distance = ((x_end - x) ** 2 + (y_end - y) ** 2) ** 0.5
            if actions.iloc[i - 1].type_name != "interception":
                if distance > 3:
                    shape = plt.Circle(
                        (x, y),
                        radius=markersize,
                        edgecolor="black",
                        linewidth=linewidth,
                        facecolor=team_color,
                        alpha=1,
                        zorder=6,
                    )
                    shapes.append(shape)
                    labels.append(
                        "ball received"
                        + "\n"
                        + action.player_name
                        + "\n"
                        + action.team_name
                    )
            line = patches.ConnectionPatch(
                (x, y),
                (x_end, y_end),
                "data",
                linestyle=":",
                color="black",
                linewidth=linewidth,
                alpha=1,
                zorder=5,
            )
            shapes.append(line)
            labels.append(
                action.type_name + "\n" + action.player_name + "\n" + action.team_name
            )

            if action.result_name == "fail":
                line = patches.ConnectionPatch(
                    (x, y),
                    (x_end, y_end),
                    "data",
                    linestyle=":",
                    color="red",
                    linewidth=linewidth * 2,
                    alpha=0.3,
                    zorder=5,
                )
                shapes.append(line)
                labels.append(
                    action.type_name
                    + "\n"
                    + action.player_name
                    + "\n"
                    + action.team_name
                )

    count = 0
    for i, (item, label) in enumerate(zip(shapes, labels)):
        patch = ax.add_patch(item)

        if isinstance(item, patches.ConnectionPatch):
            x_start, y_start = item.get_path().vertices[0]
            x_end, y_end = item.get_path().vertices[-1]
            x = (x_start + x_end) / 2
            y = (y_start + y_end) / 2
        else:
            x = item.center[0]
            y = item.center[1]

            if item.radius != 1.2:
                ax.text(
                    x,
                    y - 0.1,
                    count,
                    fontsize=fontsize,
                    color="black",
                    ha="center",
                    va="center",
                    zorder=8,
                )
                count += 1

        if with_labels:
            if isinstance(item, patches.Circle):
                if "ball received" not in label:
                    annotate = ax.annotate(
                        label,
                        xy=(x, y),
                        xytext=(10, 10),
                        textcoords="offset points",
                        color="w",
                        ha="left",
                        fontsize=fontsize,
                        zorder=8,
                        bbox=dict(
                            boxstyle="round, pad=0.5",
                            fc=(0.1, 0.1, 0.1, 0.92),
                            ec=(1.0, 1.0, 1.0),
                            lw=1,
                        ),
                    )

                    extra_height = 0.2  # Adjust this value as needed
                    bbox = annotate.get_bbox_patch()
                    bbox.set_boxstyle("round,pad=" + str(extra_height))

        ax.add_patch(patch)

    legend_elements = [
        plt.scatter(
            [],
            [],
            s=130,
            edgecolor="black",
            linewidth=linewidth,
            facecolor=MAIN_COLOR,
            zorder=5,
            marker="o",
            label=MAIN_TEAM,
        ),
        plt.scatter(
            [],
            [],
            s=130,
            edgecolor="black",
            linewidth=linewidth,
            facecolor=ALT_COLOR,
            zorder=5,
            marker="o",
            label=ALT_TEAM,
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

    goal_row = actions.iloc[len(actions) - 1]
    ax.text(
        1,
        66,
        f"{goal_row['player_name']}",
        fontsize=10,
        va="center",
        ha="left",
    )
    ax.text(
        1,
        64,
        f"{goal_row['nice_time']}",
        fontsize=10,
        va="center",
        ha="left",
    )
    ax.text(92.5, -2.1, "@francescozonaro", fontsize=10, va="center")
    plt.savefig(f"{filename}.png", format="png", bbox_inches="tight", dpi=300)


api = get_statsbomb_api()

g = 3795506
df_teams = api.teams(game_id=g)
df_players = api.players(game_id=g)
df_events = api.events(game_id=g, load_360=True)

teams = list(df_events["team_name"].unique())
teams_id = list(df_events["team_id"].unique())

df_actions = spadl.statsbomb.convert_to_actions(df_events, home_team_id=teams_id[0])
df_actions = (
    spadl.add_names(df_actions)
    .merge(api.teams(game_id=g))
    .merge(api.players(game_id=g))
)
df_actions = df_actions.sort_values(
    by=["period_id", "time_seconds"], ascending=[True, True]
).reset_index(drop=True)

MAIN_COLOR = "#bf616a"
ALT_COLOR = "#81a1c1"
MAIN_TEAM = teams[1]
ALT_TEAM = teams[0]

draw_match_goals(df_actions, with_labels=True)
