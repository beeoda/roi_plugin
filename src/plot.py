""" ROI plots in matplotlib
"""
import logging
import os

from matplotlib import use as mpl_use
mpl_use('Qt4Agg')
import matplotlib as mpl
from matplotlib.backends.backend_qt4agg \
    import FigureCanvasQTAgg as FigureCanvas

from . import data

mpl_version = map(int, mpl.__version__.split('.'))

logger = logging.getLogger('roitool')


# Note: FigureCanvas is also a QWidget
class ROIPlot(FigureCanvas):

    """ TODO
    """

    def __init__(self):
        style = os.environ.get('ROITOOL_PLOT_STYLE', 'ggplot')

        if style and mpl_version[0] >= 1 and mpl_version[1] >= 4:
            import matplotlib.style
            if style == 'xkcd':
                mpl.pyplot.xkcd()
            else:
                mpl.style.use(style)

        self.fig = mpl.figure.Figure()
        self.axis = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)

        self.setAutoFillBackground(False)
        self.plot()
        self.fig.tight_layout()

    def plot(self):
        logger.debug(data.band_names)
        # self.axis.set_xticks(range(0, len(data.band_names) + 1))
        self.axis.set_xticklabels(data.band_names, rotation=45)

        self.fig.tight_layout()
