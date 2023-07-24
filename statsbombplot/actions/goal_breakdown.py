import xml.etree.ElementTree as ET
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from io import BytesIO
from tabulate import tabulate
from statsbombplot.utils import nice_time, config, draw_pitch

def find_goal(df):
    df = df[((df['type_id'] == 11) & (df['result_id'] == 1)) | ((df['type_id'] == 12) & (df['result_id'] == 1))]
    return df.index

def draw_goals(actions):

    goals = list(find_goal(actions))

    for goal in goals:
        starting_id = goal
        df = actions[starting_id - 9: starting_id + 1].copy()
        df = df.reset_index(drop=True)
        
        df["nice_time"] = df.apply(nice_time, axis=1)
        
        cols = ['nice_time', 'player_name', 'type_name', 'result_name', 'team_name']
        
        print(tabulate(df[cols], headers = cols, showindex=True))
        draw_actions(df, filename = "test_" + str(goal))
        plt.show()

def draw_actions(actions, filename):

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