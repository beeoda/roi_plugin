""" ROI plots in matplotlib
"""
import os

import matplotlib as mpl
from matplotlib.backends.backend_qt4agg \
    import FigureCanvasQTAgg as FigureCanvas


# Note: FigureCanvas is also a QWidget
class ROIPlot(FigureCanvas):
    """ TODO
    """
    def __init__(self):
        style = os.environ.get('ROITOOL_PLOT_STYLE', 'ggplot')
        if style:
            if style == 'xkcd':
                mpl.pyplot.xkcd()
            else:
                mpl.style.use(style)

        self.fig = mpl.figure.Figure()
        self.axis = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)

        self.setAutoFillBackground(False)
        self.fig.tight_layout()

    def plot(self):
        pass
