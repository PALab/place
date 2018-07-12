"""The PLACE plotting module"""
import os.path
from random import random

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from placeweb.settings import MEDIA_ROOT

from place.config import PlaceConfig

DATA_POINT_LIMIT = int(PlaceConfig().get_config_value(
    'Plots', 'maximum points for network transfer', "10000"))
DEFAULT_FIGSIZE = (7.29, 4.17)
DEFAULT_DPI = 96


def view1(ydata1, xdata1=None):
    """Make a line chart

    This can be used to send simple line data directly to the web application
    where it will be plotted by the Elm line-charts_ library using the
    ``view1`` function.

    Here is how you would use this in your plugin during the update phase::

        from place.plots import view1

        ...

        progress['figures'] = [view1([1, 2, 3, 4])]

    .. _line-charts: http://package.elm-lang.org/packages/terezka/line-charts/1.0.0/LineChart

    :param ydata1: The y values for the series
    :type ydata1: numpy.array or list

    :param xdata1: The x values for the series (optional)
    :type xdata1: numpy.array or list or ``None``

    :returns: The data in a standard format
    :rtype: dict
    """
    data1 = _data(ydata1, xdata1)
    if len(data1['y']) > DATA_POINT_LIMIT:
        return _png([line(ydata1, xdata1)])
    return {
        'f': 'view1',
        'data1': data1
    }


def view2(ydata1, ydata2, xdata1=None, xdata2=None):
    """Make a line chart with 2 series

    This can be used to send simple line data directly to the web application
    where it will be plotted by the Elm line-charts_ library using the
    ``view2`` function.

    Here is how you would use this in your plugin during the update phase::

        from place.plots import view2

        ...

        progress['figures'] = [view2([1, 2, 3, 4], [1, 4, 9, 16])]

    .. _line-charts: http://package.elm-lang.org/packages/terezka/line-charts/1.0.0/LineChart

    :param ydata1: The y values for the first series
    :type ydata1: numpy.array or list

    :param ydata2: The y values for the second series
    :type ydata2: numpy.array or list

    :param xdata1: The x values for the first series (optional)
    :type xdata1: numpy.array or list or ``None``

    :param xdata2: The x values for the second series (optional)
    :type xdata2: numpy.array or list or ``None``

    :returns: The data in a standard format
    :rtype: dict
    """
    data1 = _data(ydata1, xdata1)
    data2 = _data(ydata2, xdata2)
    if sum([len(d['y']) for d in [data1, data2]]) > DATA_POINT_LIMIT:
        return _png([line(ydata1, xdata1),
                     line(ydata2, xdata2)])
    return {
        'f': 'view2',
        'data1': data1,
        'data2': data2
    }


def view3(ydata1, ydata2, ydata3, xdata1=None, xdata2=None, xdata3=None):
    """Make a line chart with 3 series

    This can be used to send simple line data directly to the web application
    where it will be plotted by the Elm line-charts_ library using the
    ``view3`` function.

    Here is how you would use this in your plugin during the update phase::

        from place.plots import view3

        ...

        progress['figures'] = [
            view3([1, 2, 3, 4], [1, 4, 9, 16], [1, 8, 27, 64])]

    .. _line-charts: http://package.elm-lang.org/packages/terezka/line-charts/1.0.0/LineChart

    :param ydata1: The y values for the first series
    :type ydata1: numpy.array or list

    :param ydata2: The y values for the second series
    :type ydata2: numpy.array or list

    :param ydata3: The y values for the third series
    :type ydata3: numpy.array or list

    :param xdata1: The x values for the first series (optional)
    :type xdata1: numpy.array or list or ``None``

    :param xdata2: The x values for the second series (optional)
    :type xdata2: numpy.array or list or ``None``

    :param xdata3: The x values for the third series (optional)
    :type xdata3: numpy.array or list or ``None``

    :returns: The data in a standard format
    :rtype: dict
    """
    data1 = _data(ydata1, xdata1)
    data2 = _data(ydata2, xdata2)
    data3 = _data(ydata3, xdata3)
    if sum([len(d['y']) for d in [data1, data2, data3]]) > DATA_POINT_LIMIT:
        return _png([line(ydata1, xdata1),
                     line(ydata2, xdata2),
                     line(ydata3, xdata3)])
    return {
        'f': 'view3',
        'data1': data1,
        'data2': data2,
        'data3': data3
    }


def view(series, as_png=False):
    """Show any amount of lines

    This can be used to send any number of series directly to the web
    application where it will be plotted by the Elm line-charts_ library
    using the ``view`` function.

    Here is how you would use this in your plugin during the update phase::

        from place.plots import line, view

        ...

        line1 = line([1, 2, 3, 4], label='x')
        line2 = line([1, 4, 9, 16], label='x squared')
        line3 = line([1, 8, 27, 64], label='x cubed')
        line4 = dash([1, 16, 81, 256], color=pink, label='x "quarted"')
        progress['figures'] = [view([line1, line2, line3, line4])]

    .. _line-charts: http://package.elm-lang.org/packages/terezka/line-charts/1.0.0/LineChart

    :param series: This should be a list of dictionaries output from the ``line`` function.
    :type series: list

    :param as_png: send a PNG file instead of JSON *(Default: False)*
    :type as_png: bool
    """
    if as_png or sum([len(s['data']['y']) for s in series]) > DATA_POINT_LIMIT:
        return _png(series)
    return {
        'f': 'view',
        'series': series
    }


def line(ydata, xdata=None, color='blue', shape='none', label='data'):
    """Customize a solid line

    This can be used to construct line data, used to build series.

    Colors: pink, blue, gold, red, green, cyan, teal, purple, rust,
    strongBlue, pinkLight, blueLight, goldLight, redLight, greenLight,
    cyanLight, tealLight, purpleLight, black, gray, grayLight, grayLightest,
    transparent

    Shapes: none, circle, triangle, square, diamond, plus, cross

    : param ydata: The y values for the series
    : type ydata: numpy.array

    : param xdata: The x values for the series(optional)
    : type xdata: numpy.array

    : param color: The color of the line *(Default: blue)*
    : type color: str

    : param shape: The shape of the points *(Default: none)*
    : type shape: str

    : param label: The label of the series for the legend *(Default: data)*
    : type label: str

    : returns: The series data in a standard format
    : rtype: dict
    """
    return {
        'f': 'line',
        'color': color,
        'shape': shape,
        'label': label,
        'data': _data(ydata, xdata)
    }


def dash(ydata, xdata=None, color='blue', shape='none', label='data', stroke_dasharray=None):
    """Customize a dashed line

    This can be used to construct line data, used to build series.

    Colors: pink, blue, gold, red, green, cyan, teal, purple, rust,
    strongBlue, pinkLight, blueLight, goldLight, redLight, greenLight,
    cyanLight, tealLight, purpleLight, black, gray, grayLight, grayLightest,
    transparent

    Shapes: none, circle, triangle, square, diamond, plus, cross

    : param ydata: The y values for the series
    : type ydata: numpy.array

    : param xdata: The x values for the series(optional)
    : type xdata: numpy.array

    : param color: The color of the line *(Default: blue)*
    : type color: str

    : param shape: The shape of the points *(Default: none)*
    : type shape: str

    : param label: The label of the series for the legend *(Default: data)*
    : type label: str

    : param stroke_dasharray: The float array to create dashed effect (see:
                              https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-dasharray)
    : type stroke_dasharray: list(float)

    : returns: The series data in a standard format
    : rtype: dict
    """
    if stroke_dasharray is None:
        stroke_dasharray = [2.0]
    return {
        'f': 'dash',
        'color': color,
        'shape': shape,
        'label': label,
        'stroke_dasharray': stroke_dasharray,
        'data': _data(ydata, xdata)
    }


def png(fig, alt="PLACE figure"):
    """Register a figure to be sent to PLACE as a PNG file

    It is recommended you use the PLACE defaults for `figsize` and `dpi`,
    unless you know you want something different. These defaults are
    available as `place.plots.DEFAULT_FIGSIZE` and `place.plots.DEFAULT_DPI`.

    :param fig: the figure to render as a PNG
    :type fig: matplotlib.figure.Figure

    :param alt: alt text to show if the image cannot be displayed
    :type alt: str
    """
    directory = 'figures/tmp/'
    if not os.path.exists(os.path.join(MEDIA_ROOT, directory)):
        os.makedirs(os.path.join(MEDIA_ROOT, directory))
    src = os.path.join(directory, '{}.png'.format(str(random())[2:]))
    path = os.path.join(MEDIA_ROOT, src)
    with open(path, 'wb') as file_path:
        fig.savefig(file_path, format='png')
    return {'f': 'png', 'image': {'src': src, 'alt': alt}}


def _data(ydata, xdata=None):
    if xdata is None:
        xdata = [n for n in range(len(ydata))]
    if isinstance(ydata, list):
        ydata = np.array(ydata)
    if isinstance(xdata, list):
        xdata = np.array(xdata)
    return {
        'x': xdata.astype(float, casting='same_kind').tolist(),
        'y': ydata.astype(float, casting='same_kind').tolist(),
    }


def _png(series):
    """Make a PNG file instead of sending all the data to PLACE."""
    fig = Figure(figsize=DEFAULT_FIGSIZE, dpi=DEFAULT_DPI)
    FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax.set_title('Number of points exceeded threshold: PNG rendered instead')
    for ser in series:
        ax.plot(ser['data']['x'], ser['data']['y'])
    return png(fig)
