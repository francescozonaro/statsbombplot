"""

Created on Sun Apr 19 2020

@author: Sergio Llana (@SergioMinuto90)

"""

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from io import BytesIO
from tabulate import tabulate

config = {
  "background_color": "white",
  "lines_color": "#bcbcbc",
  "edges_cmap": "Oranges",
  "nodes_cmap": "Reds",
  "font_color": "black",

  "plot_edges": True,
  "fig_size": 15,
  "font_size": 9,
  "width": 105,
  "height": 68,

  "max_node_size": 100,
  "min_node_size": 25,
  "max_edge_width": 5,
  "min_edge_width": 1
}

height = float(config["height"])
width = float(config["width"])

def _point_to_meters(p):
    '''
    Convert a point's coordinates from a 0-1 range to meters.
    '''
    return np.array([p[0]*width, p[1]*height])

def _meters_to_point(p):
    '''
    Convert a point's coordinates from meters to a 0-1 range.
    '''
    return np.array([p[0]/width, p[1]/height])

def _change_range(value, old_range, new_range):
    '''
    Convert a value from one range to another one, maintaining ratio.
    '''
    return ((value-old_range[0]) / (old_range[1]-old_range[0])) * (new_range[1]-new_range[0]) + new_range[0]

def draw_pitch(min_x=0, max_x=1):
    """
    Plot an empty horizontal football pitch, returning Matplotlib's ax object so we can keep adding elements to it.

    Parameters
    -----------
        min_x: float value from 0 to 'max_x' to choose a subsection of the pitch. Default value is 0.
        max_x: float value from 'min_x' to 1 to choose a subsection of the pitch. Default value is 1.

    Returns
    -----------
       ax : Matplotlib's axis object to keep adding elements on the pitch.
    """
    
    background_color = config["background_color"]
    lines_color = config["lines_color"]
    fig_size = config["fig_size"]

    # This allows to plot a subsection of the pitch
    ratio = height / float((width * max_x)-(width * min_x))
    f, ax = plt.subplots(1, 1, figsize=(fig_size, fig_size*ratio), dpi=600)

    ax.set_ylim([0-5, height+5])
    ax.set_xlim([width*min_x-5, width*max_x+5])
    ax.add_patch(patches.Rectangle((0, 0), width, height, color=background_color))

    # Plot outer lines
    line_pts = [
        [_point_to_meters([0, 0]), _point_to_meters([0, 1])],  # left line
        [_point_to_meters([1, 0]), _point_to_meters([1, 1])],  # right line
        [_point_to_meters([0, 1]), _point_to_meters([1, 1])],  # top line
        [_point_to_meters([0, 0]), _point_to_meters([1, 0])],  # bottom line
    ]

    for line_pt in line_pts:
        ax.plot([line_pt[0][0], line_pt[1][0]], [line_pt[0][1], line_pt[1][1]], '-',
                alpha=0.8, lw=1.5, zorder=3, color=lines_color)

    # Plot boxes
    line_pts = [
        [_point_to_meters([0.5, 0]), _point_to_meters([0.5, 1])],  # center line

        # left box
        [[0, 24.85], [0, 2.85]],
        [[0, 13.85], [16.5, 13.85]],
        [[0, 54.15], [16.5, 54.15]],
        [[16.5, 13.85], [16.5, 54.15]],

        # left goal
        [[0, 24.85], [5.5, 24.85]],
        [[0, 43.15], [5.5, 43.15]],
        [[5.5, 24.85], [5.5, 43.15]],
        [[0.2, 29.85], [0.2, 38.15]],

        # right box
        [[105, 24.85], [105, 2.85]],
        [[105, 13.85], [88.5, 13.85]],
        [[105, 54.15], [88.5, 54.15]],
        [[88.5, 13.85], [88.5, 54.15]],

        # right goal
        [[105, 24.85], [99.5, 24.85]],
        [[105, 43.15], [99.5, 43.15]],
        [[99.5, 24.85], [99.5, 43.14]],
        [[104.8, 29.85], [104.8, 38.15]]
    ]

    for line_pt in line_pts:
        ax.plot([line_pt[0][0], line_pt[1][0]], [line_pt[0][1], line_pt[1][1]], '-',
                alpha=0.8, lw=1.5, zorder=3, color=lines_color)

    # Plot circles
    ax.add_patch(patches.Wedge((94.0, 34.0), 9, 130, 230, fill=True, edgecolor=lines_color,
                               facecolor=lines_color, zorder=4, width=0.02, alpha=0.8))

    ax.add_patch(patches.Wedge((11.0, 34.0), 9, 310, 50, fill=True, edgecolor=lines_color,
                               facecolor=lines_color, zorder=4, width=0.02, alpha=0.8))

    ax.add_patch(patches.Wedge((52.5, 34), 9.5, 0, 360, fill=True, edgecolor=lines_color,
                               facecolor=lines_color, zorder=4, width=0.02, alpha=0.8))

    plt.axis('off')
    return ax

"""
Modified Jun 24 2023

@author: Francesco Zonaro

"""

def find_goal(df):
    df = df[((df['type_id'] == 11) & (df['result_id'] == 1)) | ((df['type_id'] == 12) & (df['result_id'] == 1))]
    return df.index

def nice_time(row):
    minute = int((row.period_id-1)*45 +row.time_seconds // 60)
    second = int(row.time_seconds % 60)
    return f"{minute}m{second}s"

def draw_passing_network(df_events, team_id):

    df_team = df_events[df_events['team_id'] == team_id].copy()
    index_first_sub = df_team[df_team.type_name == "Substitution"].index.min()
    df_events_pre_sub = df_team[df_team.index < index_first_sub]
    df_passes = df_events_pre_sub[df_events_pre_sub.type_name == "Pass"]
    df_received = df_passes[df_passes['extra'].apply(lambda x: 'pass' in x and 'outcome' in x['pass']) == False].reset_index(drop=True)
    df_received['receiver'] = df_received['extra'].apply(lambda x: x.get('pass', {}).get('recipient', {}).get('name'))
    df_received['location_end'] = df_received['extra'].apply(lambda x: x.get('pass', {}).get('end_location'))


    df = df_received.copy()

    df[['x', 'y']] = pd.DataFrame(df['location'].tolist())
    df[['x_end', 'y_end']] = pd.DataFrame(df['location_end'].tolist())

    df["x"] = df["x"].apply(lambda value: _change_range(value, [0, max(df.x)], [0, 105]))
    df["y"] = df["y"].apply(lambda value: _change_range(value, [0, max(df.y)], [0, 68]))
    df["x_end"] = df["x_end"].apply(lambda value: _change_range(value, [0, max(df.x_end)], [0, 105]))
    df["y_end"] = df["y_end"].apply(lambda value: _change_range(value, [0, max(df.y_end)], [0, 68]))

    df = df[['player_name', 'x', 'y', 'receiver', 'x_end', 'y_end']]

    player_pass_count = df.groupby('player_name').size().to_frame("num_passes")

    df['pair_key'] = df.apply(lambda x: "_".join(sorted([x['player_name'], x['receiver']])), axis = 1)
    pair_pass_count = df.groupby('pair_key').size().to_frame("num_passes")
    pair_pass_count = pair_pass_count[pair_pass_count['num_passes'] > 3]
    player_position = df.groupby('player_name').agg({"x" : "mean", "y" : "mean"})

    figsize_ratio = config['fig_size']/12
    ax = draw_pitch()

    max_player_count = player_pass_count.num_passes.max()
    max_pair_count = pair_pass_count.num_passes.max()

    for pair_key, row in pair_pass_count.iterrows():
        player1, player2 = pair_key.split("_")

        player1_x = player_position.loc[player1]['x']
        player1_y = player_position.loc[player1]['y']

        player2_x = player_position.loc[player2]['x']
        player2_y = player_position.loc[player2]['y']

        num_passes = row["num_passes"]

        line_width = num_passes/max_pair_count

        ax.plot([player1_x, player2_x], [player1_y, player2_y], linestyle='-', alpha = 0.4, lw = 2.5*line_width*figsize_ratio, zorder = 3, color = 'purple')


    for player_name, row in player_pass_count.iterrows():
        player_x = player_position.loc[player_name]['x']
        player_y = player_position.loc[player_name]['y']

        num_passes = row["num_passes"]

        marker_size = num_passes/max_player_count

        ax.plot(player_x, player_y, '.', markersize = 100*(marker_size)*figsize_ratio, color = 'purple', zorder=5)
        ax.plot(player_x, player_y, '.', markersize = 100*(marker_size)*figsize_ratio - 15*(marker_size)*figsize_ratio, color = 'white', zorder = 6)
        ax.annotate(player_name.split()[-1], xy=(player_x, player_y), ha='center', va='center', zorder=7, weight='bold', size = 8*figsize_ratio, path_effects=[pe.withStroke(linewidth = 2, foreground = 'white')])

def draw_goals(actions):

    goals = list(find_goal(actions))

    for goal in goals:
        starting_id = goal
        df = actions[starting_id - 9: starting_id + 1].copy()
        df = df.reset_index(drop=True)
        
        df["nice_time"] = df.apply(nice_time, axis=1)
        
        cols = ['nice_time', 'player_name', 'type_name', 'result_name', 'team_name']
        
        print(tabulate(df[cols], headers = cols, showindex=True))
        draw_svg_actions(df, filename = "test_" + str(goal))
        plt.show()

def draw_svg_actions(actions, filename):

    ET.register_namespace("", "http://www.w3.org/2000/svg")

    figsize_ratio = config['fig_size']/12
    ax = draw_pitch()

    shapes = []
    labels = []

    for i, action in actions.iterrows():

            x = action['start_x']
            x_end = action['end_x']
            y = action['start_y']
            y_end = action['end_y']

            markersize = 1 * figsize_ratio
            linewidth = 1 * figsize_ratio
            fontsize = 6 * figsize_ratio

            if i >= 1:
                if (actions.iloc[i-1].result_name == "success") & (action.type_name != "shot_penalty"):
                    x = actions.iloc[i-1].end_x
                    y = actions.iloc[i-1].end_y

            # Symbol + Line

            if (action.type_name != "dribble") & (action.type_name != "foul"):
                shape = plt.Circle((x, y), radius=markersize, edgecolor='black', linewidth=linewidth, facecolor='white', alpha=1, zorder=6)
                shapes.append(shape)
                labels.append(action.type_name + "\n" + action.player_name + "\n" + action.team_name)
                line = patches.ConnectionPatch((x, y), (x_end, y_end), 'data', linestyle='-', color='black', linewidth=linewidth, zorder=5)
                shapes.append(line)
                labels.append(action.type_name + "\n" + action.player_name + "\n" + action.team_name)

                if action.result_name == 'fail':
                    shape = plt.Circle((x, y), radius=markersize*1.2, edgecolor='red', linewidth=linewidth, facecolor='red', alpha=0.3, zorder=5)
                    shapes.append(shape)
                    labels.append(action.type_name + "\n" + action.player_name + "\n" + action.team_name)
                    line = patches.ConnectionPatch((x, y), (x_end, y_end), 'data', linestyle='-', color='red', linewidth=linewidth*2, alpha=0.3, zorder=5)
                    shapes.append(line)
                    labels.append(action.type_name + "\n" + action.player_name + "\n" + action.team_name)

            elif action.type_name == "dribble":
                line = patches.ConnectionPatch((x, y), (x_end, y_end), 'data', linestyle=':', color='black', linewidth=linewidth, alpha=1, zorder=6)
                shapes.append(line)
                labels.append(action.type_name + "\n" + action.player_name + "\n" + action.team_name)

                if action.result_name == 'fail':
                    line = patches.ConnectionPatch((x, y), (x_end, y_end), 'data', linestyle=':', color='red', linewidth=linewidth*2, alpha=0.3, zorder=5)
                    shapes.append(line)
                    labels.append(action.type_name + "\n" + action.player_name + "\n" + action.team_name)
    
    count = 0
    for i, (item, label) in enumerate(zip(shapes, labels)):
        patch = ax.add_patch(item)
        
        if isinstance(item, patches.ConnectionPatch):
            x_start, y_start = item.get_path().vertices[0]
            x_end, y_end = item.get_path().vertices[-1]

            # Calculate the center point
            x = (x_start + x_end) / 2
            y = (y_start + y_end) / 2
        else:
            x = item.center[0]
            y = item.center[1]

            if item.get_facecolor() != (1.0, 0.0, 0.0, 0.3):
                ax.text(x, y-0.1, count, fontsize=fontsize, color='black', ha='center', va='center',zorder=8)
                count += 1

        annotate = ax.annotate(label, xy=(x,y), xytext=(10,10),
                            textcoords='offset points', color='w', ha='left',
                            fontsize=fontsize, zorder=8, bbox=dict(boxstyle='round, pad=0.5',
                                                    fc=(.1, .1, .1, .92),
                                                    ec=(1., 1., 1.), lw=1))
        
        extra_height = 0.2  # Adjust this value as needed
        bbox = annotate.get_bbox_patch()
        bbox.set_boxstyle("round,pad=" + str(extra_height))

        # Add text inside the circle
        ax.add_patch(patch)
        patch.set_gid(f'mypatch_{i:03d}')
        annotate.set_gid(f'mytooltip_{i:03d}')

    f = BytesIO()
    plt.savefig(f, format="svg")

    # --- Add interactivity ---

    # Create XML tree from the SVG file.
    tree, xmlid = ET.XMLID(f.getvalue())
    tree.set('onload', 'init(event)')

    for i in shapes:
        # Get the index of the shape
        index = shapes.index(i)
        # Hide the tooltips
        tooltip = xmlid[f'mytooltip_{index:03d}']
        tooltip.set('visibility', 'hidden')
        # Assign onmouseover and onmouseout callbacks to patches.
        mypatch = xmlid[f'mypatch_{index:03d}']
        mypatch.set('onmouseover', "ShowTooltip(this)")
        mypatch.set('onmouseout', "HideTooltip(this)")

    # This is the script defining the ShowTooltip and HideTooltip functions.
    script = """
        <script type="text/ecmascript">
        <![CDATA[

        function init(event) {
            if ( window.svgDocument == null ) {
                svgDocument = event.target.ownerDocument;
                }
            }

        function ShowTooltip(obj) {
            var cur = obj.id.split("_")[1];
            var tip = svgDocument.getElementById('mytooltip_' + cur);
            tip.setAttribute('visibility', "visible")
            }

        function HideTooltip(obj) {
            var cur = obj.id.split("_")[1];
            var tip = svgDocument.getElementById('mytooltip_' + cur);
            tip.setAttribute('visibility', "hidden")
            }

        ]]>
        </script>
        """

    # Insert the script at the top of the file and save it.
    tree.insert(0, ET.XML(script))
    ET.ElementTree(tree).write(f'{filename}.svg')