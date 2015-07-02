""" ROI plots in matplotlib
"""
import logging
import os

from matplotlib import use as mpl_use
mpl_use('Qt4Agg')
import matplotlib as mpl
from matplotlib.backends.backend_qt4agg \
    import FigureCanvasQTAgg as FigureCanvas
import numpy as np

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

    def plot(self, stats=None):
        """ Plot ROI statistics

        Args:
          stats (dict, optional): Statistics grouped by the ROI class label.
            Each value in dict contains a dict of statistical
            attributes listed by band

        Example:
            stats['forest'] = {
                'mean': [10, 20, 10, 60, 25, 15],
                'std': [3, 5, 3, 10, 5, 5]
            }

        """
        logger.debug(data.band_names)
        x_ticks = np.arange(len(data.band_names)) + 0.5
        if stats is None:
            self.axis.plot(x_ticks, np.zeros(len(data.band_names)), 'none')
        else:
            # TODO: plot means
            # TODO: plot std bars
            # TODO: legend (outside or inside?)
            from PyQt4 import QtCore
            QtCore.pyqtRemoveInputHook()
            from IPython.core.debugger import Pdb
            Pdb().set_trace()

        self.axis.set_xticks(x_ticks)
        self.axis.set_xticklabels(data.band_names, rotation=45)

        self.fig.tight_layout()
