# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ROITool
                                 A QGIS plugin
 QGIS Plugin for exploring the spectral signatures of ROIs
                             -------------------
        begin                : 2015-06-23
        copyright            : (C) 2015 by Eric Bullock, Chris Holden
        email                : bullocke@bu.edu
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ROITool class from file ROITool.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .roitool import ROITool
    return ROITool(iface)
