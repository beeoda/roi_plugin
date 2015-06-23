# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ROIToolDialog
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

from PyQt4 import QtGui

from ui_roitool_dialog import Ui_ROIToolDialog

from .logger import qgis_log

logger = logging.getLogger('roitool')



class ROIToolDialog(QtGui.QDialog, Ui_ROIToolDialog):
    def __init__(self, iface, parent=None):
        super(ROIToolDialog, self).__init__(parent)
        self.setupUi(self)

        self.iface = iface

        qgis_log('Loaded plugin', logging.INFO)

    def unload(self):
        pass
