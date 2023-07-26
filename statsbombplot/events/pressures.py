import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from io import BytesIO
from statsbombplot.utils import config, draw_pitch, change_range
import matplotlib.patches as mpatches

def draw_pressures(events, filename, title=""):

    ET.register_namespace("", "http://www.w3.org/2000/svg")

    figsize_ratio = config['fig_size']/12
    ax = draw_pitch()

    shapes = []
    labels = []

    for i, event in events.iterrows():

            markersize = 1 * figsize_ratio
            linewidth = 1 * figsize_ratio
            fontsize = 6 * figsize_ratio

            # Statsbomb pitch dimensions: 120 length, 80 width

            x = change_range(event.location[0], [0, 120], [0, 105])
            y = change_range(event.location[1], [0, 80], [0, 68])

            triangle_side_length = markersize

            # Calculate the vertices of the triangle based on the center position
            x1, y1 = x, y + triangle_side_length / (3 ** 0.5)
            x2, y2 = x - triangle_side_length / 2, y - triangle_side_length / (2 * (3 ** 0.5))
            x3, y3 = x + triangle_side_length / 2, y - triangle_side_length / (2 * (3 ** 0.5))

            # Create a Polygon object representing the triangle
            vertices = [(x1, y1), (x2, y2), (x3, y3)]
            shape = plt.Polygon(vertices, closed=True, edgecolor='black', facecolor=(0.765, 0.388, 0.961, 0.8), linewidth=linewidth/2, zorder=5)
            shapes.append(shape)
            labels.append(event.type_name + "\n" + 
                          event.player_name + "\n" + 
                          event.play_pattern_name + "\n" +
                          str(event.minute) + ":" + '{:02d}'.format(event.second)
                          )


    for i, (item, label) in enumerate(zip(shapes, labels)):
        patch = ax.add_patch(item)

        # x = item.center[0]
        # y = item.center[1]
        x,y = item.get_xy().mean(axis=0)
        xtext = 10
        ytext = 10

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

    events['X'] = events['location'].apply(lambda loc: loc[0])
    events['Y'] = events['location'].apply(lambda loc: loc[1])

    # Group by the 'event_id' and calculate the mean X and Y for each ball recovery
    mean_coordinates = events[['X', 'Y']].mean()
    avg_ball_recovery_x = change_range(mean_coordinates.X, [0, 120], [0, 105])

    vertical_line = mpatches.ConnectionPatch((avg_ball_recovery_x, 0.1), (avg_ball_recovery_x, 67.9), "data", "data", edgecolor=(0.88, 0.48, 0.37, 0.8), linewidth=2, zorder=7, linestyle='dashed')
    ax.add_patch(vertical_line)

    # recovery_patch = mpatches.Circle((1, -2), radius=1, facecolor="purple", edgecolor='black', label='Recovery')
    recovery_patch = mpatches.RegularPolygon((2, -2.1), numVertices=3, radius=1, facecolor=(0.765, 0.388, 0.961, 0.8), edgecolor='black', label='Recovery', linewidth=linewidth)
    attacking_direction_patch = mpatches.FancyArrowPatch((35, -2), (35 + 10, -2),
                                arrowstyle='->', mutation_scale=10, linewidth=1, color='black')
    mean_height_recovery = mpatches.FancyArrowPatch((70, -2), (70 + 10, -2),
                                arrowstyle='-', mutation_scale=10, linewidth=2, color=(0.88, 0.48, 0.37, 0.8), linestyle="dashed")
    
    legend_elements = [recovery_patch, attacking_direction_patch, mean_height_recovery]
    labels = ['Press. Action', 'Attacking Direction', 'Mean Height of Press. Action']
    labels_x_position = [3.5, 20, 49]

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
