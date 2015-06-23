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
import os

from PyQt4 import QtCore, QtGui

# Initialize Qt resources from file resources.py
import resources_rc

from roitool_dialog import ROIToolDialog


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

        # Initialize dialog in a dock
        self.dialog = ROIToolDialog(self.iface)

        self.dock = QtGui.QDockWidget('ROI Tool', self.iface.mainWindow())
        self.dock.setObjectName('ROI Tools')
        self.dock.setWidget(self.dialog)

        self.iface.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                                 self.dock)

    def initGui(self):
        """ Create and load toolbar icon for plugin inside QGIS
        """
        # MapTool button
        self.action = QtGui.QAction(
            QtGui.QIcon(':/plugins/roitool/media/icon.png'),
            'ROI Tool',
            self.iface.mainWindow())
        self.action.triggered.connect(self.show_dialog)
        self.iface.addToolBarIcon(self.action)

    def show_dialog(self):
        self.dialog.show()

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dialog.show()
        # Run the dialog event loop
        result = self.dialog.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def unload(self):
        """ Shutdown and disconnect """
        # Disconnect action
        self.action.triggered.disconnect()

        # Close dialog
        self.dialog.unload()
        self.dialog.close()
        self.dialog = None

        # Remove dock widget
        self.iface.removeDockWidget(self.dock)
        self.dock.deleteLater()
        self.dock = None

        # Remove toolbar icons
        self.iface.removeToolBarIcon(self.action)
