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
        numBands = len(data.band_names) - 1
        self.axis.clear()
        x_ticks = np.arange(numBands) + 0.5
        if stats is None:
            self.axis.plot(x_ticks, np.zeros(numBands), 'ro')
        else:
            for k in stats:
                self.axis.errorbar(x_ticks, stats[k]['mean'],
                                   yerr=stats[k]['std'], label=k,
                                   fmt='--o', lw=3, markersize=7.5,
                                   capsize=5, capthick=3,
                                   markeredgecolor='none',
                                   picker=3)
            self.axis.legend(loc='best', # bbox_to_anchor=(0.5, 1.05),
                             ncol=2, fancybox=True, fontsize='x-large',
                             numpoints=1)

        self.axis.set_xlim([0, numBands])
        self.axis.set_xticks(x_ticks)
        self.axis.set_xticklabels(data.band_names, rotation=45)

        self.axis.set_xlabel('Raster Bands')
        self.axis.set_ylabel(r'Mean $\pm$ Standard Deviation', rotation=90)

        self.fig.tight_layout()
        self.fig.canvas.draw()
