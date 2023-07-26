import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
from statsbombplot.utils import config, draw_pitch, change_range
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors

def draw_star(center, size):
    angles = np.linspace(0, 2 * np.pi, 7)[:-1] + np.pi / 10
    x = center[0] + size * np.cos(angles)
    y = center[1] + size * np.sin(angles)
    return list(zip(x, y))

def draw_shotmap(events, filename, team_left_id, title=""):

    ET.register_namespace("", "http://www.w3.org/2000/svg")

    figsize_ratio = config['fig_size']/12
    ax = draw_pitch()

    shapes = []
    labels = []
    teams = []

    for i, event in events.iterrows():

            markersize = 1 * figsize_ratio
            linewidth = 1 * figsize_ratio
            fontsize = 6 * figsize_ratio
            shot_xG = round(event.extra['shot']['statsbomb_xg'],3)
            alpha_xG = round(change_range(shot_xG, [0,1], [0.2,1]),3)

            shot_technique = event.extra['shot']['technique']['name']

            if shot_technique == 'Normal':
                shot_technique = event.extra['shot']['body_part']['name']

            teams.append(event.team_id)

            # Statsbomb pitch dimensions: 120 length, 80 width
            if event.team_id != team_left_id:
                x = change_range(event.location[0], [0, 120], [0, 105])
                y = change_range(event.location[1], [0, 80], [0, 68])
                shot_color = (0.88, 0.48, 0.37, alpha_xG)
            else:
                x = 105 - change_range(event.location[0], [0, 120], [0, 105])
                y = 68 - change_range(event.location[1], [0, 80], [0, 68])
                shot_color = (0.5, 0.78, 0.97, alpha_xG)

            if event.extra['shot']['outcome']['name'] == 'Goal':
                center = (x, y)
                size = markersize
                star_vertices = draw_star(center, size)
                shape = plt.Polygon(star_vertices, edgecolor='black', facecolor=shot_color, zorder = 6)
                shapes.append(shape)
                labels.append("Goal" + f" ({shot_technique})" + "\n" + event.player_name + "\n" + event.team_name + "\n" + "xG: " + str(shot_xG))
            elif event.extra['shot']['outcome']['name'] == 'Saved':
                shape = plt.Circle((x, y), radius=markersize, edgecolor='black', linewidth=linewidth, facecolor=shot_color, zorder=5)
                shapes.append(shape)
                labels.append(event.type_name + f" ({shot_technique})" +  "\n" + event.player_name + "\n" + event.team_name + "\n" + "xG: " + str(shot_xG))
            else:
                shape = plt.Circle((x, y), radius=markersize, edgecolor='black', linewidth=linewidth, facecolor=shot_color, zorder=5)
                shape.set_hatch('////')
                shapes.append(shape)
                labels.append(event.type_name + f" ({shot_technique})" + "\n" + event.player_name + "\n" + event.team_name + "\n" + "xG: " + str(shot_xG))

    for i, (item, label, team) in enumerate(zip(shapes, labels, teams)):
        patch = ax.add_patch(item)
        
        if isinstance(item, patches.Polygon):
            x_start, y_start = item.get_path().vertices[0]
            x_end, y_end = item.get_path().vertices[3]

            # Calculate the center point
            x = (x_start + x_end) / 2
            y = (y_start + y_end) / 2
        else:
            x = item.center[0]
            y = item.center[1]

        if team == team_left_id:
            xtext = 10
            ytext = 10
        else:
            xtext = -40
            ytext = -45
        
        annotate = ax.annotate(label, xy=(x,y), xytext=(xtext,ytext),
                            textcoords='offset points', color='w', ha='left',
                            fontsize=fontsize, zorder=8, bbox=dict(boxstyle='round, pad=0.7',
                                                    fc=(.1, .1, .1, .92),
                                                    ec=(1., 1., 1.), lw=1))
        
        extra_height = 0.2
        bbox = annotate.get_bbox_patch()
        bbox.set_boxstyle("round,pad=" + str(extra_height))

        ax.add_patch(patch)
        patch.set_gid(f'mypatch_{i:03d}')
        annotate.set_gid(f'mytooltip_{i:03d}')


    goal_patch = mpatches.RegularPolygon((2, -2.05), numVertices=6, radius=1, facecolor=(1, 1, 1, 0.8), edgecolor='black', label='Goal')
    saved_patch = mpatches.Circle((10, -2.05), radius=1, facecolor=(1, 1, 1, 0.8), edgecolor='black', label='Saved')
    missed_patch = mpatches.Circle((21.25, -2.05), radius=1, facecolor=(1, 1, 1, 0.8), edgecolor='black', hatch='////', label='Missed')
    
    legend_elements = [goal_patch, saved_patch, missed_patch]
    labels = ['Goal', 'On Target', 'Off Target']
    labels_x_position = [3.5, 11.5, 22.75]

    legend_y = -2.1

    for i, (legend_element, label, labels_x_position) in enumerate(zip(legend_elements, labels, labels_x_position)):
        ax.add_patch(legend_element)
        ax.text(labels_x_position, legend_y, label, fontsize=10, va='center')

    ax.text(0, 70, title, fontsize=15, va='center')
    ax.text(86.5, -2.1, 'Plotted with statsbombplot', fontsize=10, va='center')

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