import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from io import BytesIO
from statsbombplot.utils import config, draw_pitch, change_range
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

def draw_pressures(events, filename):

    figsize_ratio = config['fig_size']/12
    ax = draw_pitch()

    shapes = []
    labels = []

    for i, event in events.iterrows():

            markersize = 50 * figsize_ratio
            linewidth = 0.5 * figsize_ratio
            fontsize = 6 * figsize_ratio

            # Statsbomb pitch dimensions: 120 length, 80 width

            x = change_range(event.location[0], [0, 120], [0, 105])
            y = change_range(event.location[1], [0, 80], [0, 68])

            ax.scatter(x,y, s=markersize, edgecolor='black', linewidth=linewidth, facecolor=(0.765, 0.388, 0.961, 0.8), zorder=7, marker='^')


    events['X'] = events['location'].apply(lambda loc: loc[0])
    events['Y'] = events['location'].apply(lambda loc: loc[1])

    # Group by the 'event_id' and calculate the mean X and Y for each ball recovery
    mean_coordinates = events[['X', 'Y']].mean()
    avg_ball_recovery_x = change_range(mean_coordinates.X, [0, 120], [0, 105])

    ax.axvline(x=avg_ball_recovery_x, ymin=0.0625, ymax=0.9375, color=(0.88, 0.48, 0.37, 0.8), linewidth=2, zorder=4, linestyle='dashed')

    markersize = 50 * figsize_ratio
    linewidth = 0.5 * figsize_ratio

    legend_elements = [
        plt.scatter(x,y, s=markersize, edgecolor='black', linewidth=linewidth, facecolor=(0.765, 0.388, 0.961, 0.8), zorder=7, marker='^', label='Pressure'),
        mlines.Line2D([], [], color=(0.88, 0.48, 0.37, 0.8), linewidth=2, linestyle='dashed', label='Mean Height of Pressure')
    ]

    ax.legend(handles=legend_elements, loc='upper center', ncol=len(legend_elements),
              bbox_to_anchor=(0.5, 0.99), fontsize=10, fancybox=True, frameon=True, handletextpad=0.5)

    ax.text(92.5, -2.1, '@francescozonaro', fontsize=10, va='center')

    plt.savefig(filename, bbox_inches='tight')
