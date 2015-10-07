# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ROITool
                                 A QGIS plugin
 QGIS Plugin for exploring the spectral signatures of ROIs
                              -------------------
        begin                : 2015-06-23
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Eric Bullock, Chris Holden
        email                : bullocke@bu.edu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import logging
import os

from PyQt4 import QtCore, QtGui

# Initialize Qt resources from file resources.py
import resources_rc

from roitool_dialog import ROIToolDialog

from .logger import qgis_log

logger = logging.getLogger('roitool')


class ROITool(QtCore.QObject):
    """
    TODO
    """
    def __init__(self, iface):
        """Constructor.

        Args:
          iface (QgsInterface): An interface instance that will be passed to
            this class which provides the hook by which you can manipulate the
            QGIS application at run time.

        """
        super(ROITool, self).__init__()
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QtCore.QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n',
                                   'roitool_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QtCore.QTranslator()
            self.translator.load(locale_path)

            if QtCore.qVersion() > '4.3.3':
                QtCore.QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        """ Create QDialog and put into a dock
        """
        # Initialize dialog in a dock
        self.dialog = ROIToolDialog(self.iface)

        self.dock = QtGui.QDockWidget('ROI Explorer', self.iface.mainWindow())
        self.dock.setObjectName('ROI Explorer')
        self.dock.setWidget(self.dialog)

        self.iface.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                                 self.dock)

        # Setup action for showing/hiding plugin
        # toggleViewAction() returns QAction to show/close dock widget. See:
        # http://doc.qt.io/qt-4.8/qdockwidget.html#toggleViewAction
        self.action = self.dock.toggleViewAction()
        self.action.setIcon(QtGui.QIcon(':/plugins/roitool/media/icon.png'))
        self.action.setText('Show/hide ROI Explorer')
        self.action.setWhatsThis('Show/hide ROI Explorer plugin')

        # Add plugin to Raster menu
        if hasattr(self.iface, "addPluginToRasterMenu"):
            # Raster menu and toolbar available
            self.iface.addPluginToRasterMenu("&ROI Explorer", self.action)
            self.iface.addRasterToolBarIcon(self.action)
        else:
            # there is no Raster menu, place plugin under Plugins menu as usual
            self.iface.addPluginToMenu("&ROI Explorer", self.action)
            self.iface.addToolBarIcon(self.action)

    def unload(self):
        """ Shutdown and disconnect """
        # Close dialog
        self.dialog.unload()
        self.dialog.close()
        self.dialog = None

        # Remove dock widget
        self.iface.removeDockWidget(self.dock)
        self.dock.deleteLater()
        self.dock = None

        # Remove menu entry
        if hasattr(self.iface, "addPluginToRasterMenu"):
            # Raster menu and toolbar available
            self.iface.removePluginRasterMenu("&ROI Explorer", self.action)
            self.iface.removeRasterToolBarIcon(self.action)
        else:
            # there is no Raster menu, place plugin under Plugins menu as usual
            self.iface.removePluginMenu("&ROI Explorer", self.action)
            self.iface.removeToolBarIcon(self.action)
