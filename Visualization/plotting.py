import bokeh.models as bm, bokeh.plotting as pl
from bokeh.io import output_notebook
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

import numpy as np


def plot_points_by_bokeh(x, y, radius=10, alpha=0.25, color='blue',
                 width=600, height=400, show=True, **kwargs):
    """ draws an interactive plot for data points with auxilirary info on hover """
    if isinstance(color, str): color = [color] * len(x)
    data_source = bm.ColumnDataSource({ 'x' : x, 'y' : y, 'color': color, **kwargs })

    fig = pl.figure(active_scroll='wheel_zoom', width=width, height=height)
    fig.scatter('x', 'y', size=radius, color='color', alpha=alpha, source=data_source)

    fig.add_tools(bm.HoverTool(tooltips=[(key, "@" + key) for key in kwargs.keys()]))
    if show: pl.show(fig)
    return fig

def plot_time_dinamic(tbl, patient_id, ekg_feature):
    df = tbl[tbl['combined_id'] == patient_id]
    plt.plot(df[ekg_feature].values)
    plt.title(ekg_feature)
    
    
def plot_outliers(list_of_positive, list_of_negative, feature):
    x = np.arange(0.0, len(list_of_positive), 1.0)
    print (len(x))
    y = list_of_positive

    plt.scatter(x, y, c="r", alpha=0.5, marker=r'$\clubsuit$',
                label="Positive")

    x = np.arange(0.0, len(list_of_negative), 1.0)
    print (len(x))
    y = list_of_negative

    plt.scatter(x, y, c="g", alpha=0.5, marker=r'$\clubsuit$',
                label="Negative")
    plt.xlabel("Outliers")
    plt.ylabel(feature)
    plt.legend(loc='upper left')
    plt.show()