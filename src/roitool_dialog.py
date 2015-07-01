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
from collections import OrderedDict
from functools import partial
import logging

from PyQt4 import QtCore, QtGui

from qgis.core import (QgsMapLayer, QgsRasterLayer, QgsVectorLayer,
                       QgsMapLayerRegistry)

from ui_roitool_dialog import Ui_ROIToolDialog

from . import data
from .logger import qgis_log
from .plot import ROIPlot

logger = logging.getLogger('roitool')


class ROIToolDialog(QtGui.QDialog, Ui_ROIToolDialog):

    """ TODO
    """
    layer_dict = dict(name=None, id=None, obj=None)
    rlayers = OrderedDict()  # track raster layers as rlayer.id(): layer_dict
    vlayers = OrderedDict()  # track vector layers as vlayer.id(): layer_dict

    def __init__(self, iface, parent=None):
        super(ROIToolDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface

        self._init_gui()
        self._init_plot()

    def _init_gui(self):
        """ Initialize GUI components """
        # Populate QComboBox with raster and vector layers
        # TODO: I don't think we need to do this -- layersAdded does it
        #       Should make sure it actually works 100% of time
        #       RE: what if we enable plugin after layers added...
        #           we need to do it
        layers = QgsMapLayerRegistry.instance().mapLayers()
        if layers:
            self._map_layers_added(layers.values())
            self._rlayer_changed(self.combox_raster.currentIndex())

        # Wire map layer added/remove events
        QgsMapLayerRegistry.instance().layersAdded.connect(
            self._map_layers_added)
        QgsMapLayerRegistry.instance().layersWillBeRemoved.connect(
            self._map_layers_removed)

        # Populate and wire field QComboBox
        self.combox_field.clear()
        idx = self.combox_vector.currentIndex()
        self._vlayer_changed(idx)

        # Wire vector and raster QComboBox
        self.combox_vector.currentIndexChanged.connect(self._vlayer_changed)
        self.combox_raster.currentIndexChanged.connect(self._rlayer_changed)

        # Wire buttons
        self.but_update.clicked.connect(self._update_plot)
        self.but_saveplot.clicked.connect(self._save_plot)
        self.but_savestats.clicked.connect(self._export_data)

    def _init_plot(self):
        """ Setup plot """
        self.plot = ROIPlot()
        self.widget_plot.setLayout(QtGui.QVBoxLayout())
        self.widget_plot.layout().setContentsMargins(0, 0, 0, 0)
        self.widget_plot.layout().addWidget(self.plot)

# SIGNALS
    @QtCore.pyqtSlot(list)
    def _map_layers_added(self, layers):
        """ Keep track of newly added layers

        Adds new layers to either `self.rlayers` or `self.vlayers`.
        Adds new layers to appropriate QComboBox
        Wires QgsMapLayer rename (`layerNameChanged`) and data change signals
          (dataChanged)

        Args:
          layers (list): list of Qgs[Raster|Vector]Layer

        """
        logger.debug('Adding map layers {l}'.format(l=layers))
        for layer in layers:
            if isinstance(layer, QgsRasterLayer):
                self.rlayers[layer.id()] = dict(name=layer.name(),
                                                id=layer.id(),
                                                obj=layer)
                self.combox_raster.addItem(layer.name(), layer.id())
                layer.layerNameChanged.connect(
                    partial(self._layer_renamed, layer))
                # TODO: wire
            elif isinstance(layer, QgsVectorLayer):
                self.vlayers[layer.id()] = dict(name=layer.name(),
                                                id=layer.id(),
                                                obj=layer)
                self.combox_vector.addItem(layer.name(), layer.id())
                # Wire rename
                layer.layerNameChanged.connect(
                    partial(self._layer_renamed, layer))
                # Wire field change
                layer.updatedFields.connect(
                    partial(self._vlayer_modified, layer))
                # TODO: Wire data changed

    @QtCore.pyqtSlot(list)
    def _map_layers_removed(self, layer_ids):
        """ Keep track of removed layers

        Remove from `self.rlayers` or `self.vlayers`
        Remove QComboBox entry
        Disconnect QgsMapLayer from signals

        Args:
          layer_ids (list): list of layer IDs that have been removed
        """
        logger.debug('Removing layers: {l}'.format(l=layer_ids))
        # TODO: see docstring
        for layer_id in layer_ids:
            # Try to remove from both QComboxBox
            idx = self.combox_raster.findData(layer_id)
            self.combox_raster.removeItem(idx)
            idx = self.combox_vector.findData(layer_id)
            self.combox_vector.removeItem(idx)

    @QtCore.pyqtSlot(int)
    def _vlayer_changed(self, idx):
        """ Update when new vector layer has been selected

        Args:
          idx (int): index of `self.combox_vector` selected

        """
        logger.debug('Selected new vector: {v} (i={i})'.format(
            v=self.combox_vector.currentText(), i=idx))

        self.combox_field.clear()
        if idx == -1:
            return

        # Determine layer
        layer_id = self.combox_vector.itemData(
            self.combox_vector.currentIndex())
        layer = QgsMapLayerRegistry.instance().mapLayers()[layer_id]

        n_features = layer.featureCount()
        features = layer.getFeatures()
        fields = layer.pendingFields()

        # Update vector layer field name QComboBox
        for field in fields:
            self.combox_field.addItem(
                '{n} ({t})'.format(n=field.name(), t=field.typeName()),
                field.name())

        # TODO: update attribute table
        headers = ['FID'] + [f.name() for f in fields.toList()]
        self.table_feature.clear()
        self.table_feature.setColumnCount(len(headers))
        self.table_feature.setRowCount(n_features)
        self.table_feature.setHorizontalHeaderLabels(headers)
        self.table_feature.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)

        for i, feat in enumerate(features):
            item = QtGui.QTableWidgetItem()
            item.setData(QtCore.Qt.DisplayRole, feat.id())
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)
            self.table_feature.setItem(i, 0, item)
            for j, attr in enumerate(feat.attributes()):
                item = QtGui.QTableWidgetItem()
                item.setData(QtCore.Qt.DisplayRole, attr)
                item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                      QtCore.Qt.AlignVCenter)
                self.table_feature.setItem(i, j + 1, item)

        self.table_feature.resizeColumnsToContents()

    @QtCore.pyqtSlot(QgsVectorLayer)
    def _vlayer_modified(self, vlayer):
        """ Push an update when a vector layer has been modified

        Note that this only takes action if `vlayer` modified is one currently
        selected.

        Args:
          vlayer (QgsVectorLayer): vector layer modified

        """
        logger.debug('Vector layer {v} was modified'.format(v=vlayer.id()))
        idx = self.combox_vector.findData(vlayer.id())
        if idx == self.combox_vector.currentIndex():
            self._vlayer_changed(idx)

    @QtCore.pyqtSlot(QgsMapLayer)
    def _layer_renamed(self, layer):
        """ Keep track of renamed layers

        """
        logger.debug('Renamed layer {i}'.format(i=layer.id()))

        if isinstance(layer, QgsRasterLayer):
            idx = self.combox_raster.findData(layer.id())
            self.combox_raster.setItemText(idx, layer.name())
            self.rlayers[layer.id()]['name'] = layer.name()  # TODO: remove
        elif isinstance(layer, QgsVectorLayer):
            idx = self.combox_vector.findData(layer.id())
            self.combox_vector.setItemText(idx, layer.name())
            self.vlayers[layer.id()]['name'] = layer.name()  # TODO: remove

    @QtCore.pyqtSlot(int)
    def _rlayer_changed(self, idx):
        """
        """
        logger.debug('Selected new raster: {r} ({i})'.format(
            r=self.combox_raster.currentText(), i=idx))
        rlayer_id = self.combox_raster.itemData(idx)
        if rlayer_id:
            rlayer = QgsMapLayerRegistry.instance().mapLayers()[rlayer_id]
            data.band_names = [rlayer.bandName(i) for i in
                               range(rlayer.bandCount())]
        else:
            data.band_names = []

    @QtCore.pyqtSlot()
    def _update_plot(self):
        """ Handle plot update request
        """
        logger.debug('ROI plot update requested')
        self.plot.plot()

    @QtCore.pyqtSlot()
    def _save_plot(self):
        """ Handle a plot save request
        """
        logger.debug('ROI plot save requested')

    @QtCore.pyqtSlot()
    def _export_data(self):
        """ Handle a data export request
        """
        logger.debug('ROI data export requested')

    def unload(self):
        logger.debug('Unloading dialog')
        # Disconnect layer add/remove signals
        QgsMapLayerRegistry.instance().layersAdded.disconnect(
            self._map_layers_added)
        QgsMapLayerRegistry.instance().layersWillBeRemoved.disconnect(
            self._map_layers_removed)

        # Disconnect layers from all of our slots
        for layer in QgsMapLayerRegistry.instance().mapLayers().itervalues():
            if layer.receivers(QtCore.SIGNAL('layerNameChanged()')) > 0:
                try:
                    layer.layerNameChanged.disconnect(self._layer_renamed)
                except:
                    pass
            if layer.receivers(QtCore.SIGNAL('updatedFields()')) > 0:
                try:
                    layer.updatedFields.disconnect(self._vlayer_modified)
                except:
                    pass

        # Disconnect remaining UI elements
        self.combox_vector.currentIndexChanged.disconnect(self._vlayer_changed)
        self.combox_raster.currentIndexChanged.disconnect(self._rlayer_changed)

        self.but_update.clicked.disconnect(self._update_plot)
        self.but_saveplot.clicked.disconnect(self._save_plot)
        self.but_savestats.clicked.disconnect(self._export_data)
