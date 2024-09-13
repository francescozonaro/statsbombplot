import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
from tabulate import tabulate

from utils import Pitch
from .matchBase import BaseMatchSBP


class GoalBreakdownSBP(BaseMatchSBP):

    def __init__(self):
        super().__init__()

    def _nice_time(self, row):
        minute = int((row.period_id - 1) * 45 + row.time_seconds // 60)
        second = int(row.time_seconds % 60)
        return f"{minute}m{second}s"

    def _find_goal(self, df):
        df = df[
            ((df["type_id"] == 11) & (df["result_id"] == 1))
            | ((df["type_id"] == 12) & (df["result_id"] == 1) & (df["period_id"] < 5))
            | (df["result_id"] == 3)
        ]
        return df.index

    def _draw_match_goals(self, actions, home_team, with_labels=True):

        goals = list(self._find_goal(actions))

        for goal in goals:
            starting_id = goal
            df = actions[starting_id - 9 : starting_id + 1].copy()
            df = df.reset_index(drop=True)

            df["nice_time"] = df.apply(self._nice_time, axis=1)

            cols = ["nice_time", "player_name", "type_name", "result_name", "team_name"]

            print(tabulate(df[cols], headers=cols, showindex=True))
            self._draw_actions(df, "imgs/test_" + str(goal), with_labels, home_team)

    def _draw_actions(self, actions, filename, with_labels, home_team):

        pitch = Pitch()
        f, ax = pitch.draw()

        pass

    def draw(self, g, events, teams, players):

        teams_id = list(teams["team_id"])

        self._draw_match_goals(
            events,
            teams_id[0],
            with_labels=True,
        )
