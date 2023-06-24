"""

Created on Sun Apr 19 2020

@author: Sergio Llana (@SergioMinuto90)

Modified Jun 24 2023

@author: Francesco Zonaro

"""

from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

config = {
  "background_color": "white",
  "lines_color": "#bcbcbc",
  "edges_cmap": "Oranges",
  "nodes_cmap": "Reds",
  "font_color": "black",

  "plot_edges": True,
  "fig_size": 12,
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

def draw_actions(ax, actions, title="", legend=""):

    shots_color = "#AA4A44"
    passes_color = "#96DB8F"
    throws_color = passes_color
    dribbles_color = "#C18FDB"
    tackles_color = "#DB9B2A"
    fouls_color = "#FA8416"

    passes_cmap = LinearSegmentedColormap.from_list('custom_cmap', [(0, (0, 0, 0, 0)), (1, passes_color)])

    shots = actions[actions['type_name'] == 'shot']
    passes = actions[(actions['type_name'] == 'pass')]
    throws = actions[actions['type_name'] == 'throw_in']
    dribbles = actions[actions['type_name'] == 'dribble']
    tackles = actions[actions['type_name'] == 'tackle']
    fouls = actions[actions['type_name'] == 'foul']
    shortfks = actions[actions['type_name'] == 'freekick_short']

    # Plot shots
    ax.plot(shots['start_x'], shots['start_y'], 
            '.',  
            color=shots_color,
            markersize=20, 
            zorder=4)

    # Plot passes
    ax.plot(passes['start_x'], passes['start_y'], 
            '.',  
            color=passes_color,
            markersize=20, 
            zorder=4)
    ax.plot([passes['start_x'], passes['end_x']],
            [passes['start_y'], passes['end_y']],
            linestyle="-",
            color = passes_color,
            linewidth=2,
            zorder=3,
            )
    
    # Plot throw ins
    ax.plot(throws['start_x'], throws['start_y'], 
            's',  
            color=throws_color,
            markersize=10, 
            zorder=4)
    ax.plot([throws['start_x'], throws['end_x']],
            [throws['start_y'], throws['end_y']],
            linestyle="-",
            color=throws_color,
            linewidth=2,
            zorder=3
            )

    # Plot dribbles
    ax.plot([dribbles['start_x'], dribbles['end_x']],
            [dribbles['start_y'], dribbles['end_y']],
            linestyle=":",
            color=dribbles_color,
            linewidth=2,
            zorder=3
            )
    
    # Plot tackles
    ax.plot(tackles['start_x'], tackles['start_y'], 
            '^',  
            color=tackles_color,
            markersize=10, 
            zorder=4)
    
    # Plot fouls
    ax.plot(fouls['start_x'], fouls['start_y'], 
            '+',  
            color=fouls_color,
            markersize=10, 
            zorder=4)
    
    # Plot short freekicks
    ax.plot([shortfks['start_x'], shortfks['end_x']],
            [shortfks['start_y'], shortfks['end_y']],
            linestyle="-",
            color=passes_color,
            linewidth=2,
            zorder=3
            )