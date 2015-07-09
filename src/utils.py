""" Miscellaneous utility functions for plugin use
"""
import re, ogr, osr

from osgeo import gdal
import numpy as np


def abbreviate_band_name(name):
    """ Return an abbreviated version of a band name

    Args:
      name (str): name to abbreviate

    Returns:
      str: abbreviated name

    """
    # Abbreviate "Surface Reflectance"
    name = re.sub('(?i)surface.*refl[a-z]*', 'SR', name)
    # Abbreviate "Top of Atmosphere"
    name = re.sub('(?i)top.*atmo[a-z]*', 'TOA', name)
    # Abbreviate lingering "reflectance"
    name = re.sub('(?i)refl[a-z]*', 'refl', name)
    # Abbreviate temperature
    name = re.sub('(?i)temp[a-z]*', 'temp', name)
    # Abbreviate "Near Infrared" or "Shortwave Infrared"
    name = re.sub('(?i)near.*infrared', 'NIR', name)
    name = re.sub('(?i)short.*infrared', 'SWIR', name)
    # Abbreviate "Band #"
    name = re.sub('(?i)band *', 'B', name)

    return name


def get_band_names(rlayer):
    """ Returns a list of band names from a raster file

    Returns band names using band descriptions if available; else return
    "Band 1", ..., "Band N".

    Args:
      rlayer (QgsRasterLayer): QGIS raster layer object

    Returns:
      list: list of `str` containing band names

    """
    try:
        ds = gdal.Open(rlayer.source(), gdal.GA_ReadOnly)
    except:
        return [rlayer.bandName(i) for i in range(1, rlayer.bandCount() + 1)]
    else:
        band_names = []
        for i in range(ds.RasterCount):
            band = ds.GetRasterBand(i + 1)
            if band.GetDescription():
                band_names.append(abbreviate_band_name(band.GetDescription()))
            else:
                band_names.append(rlayer.bandName(i + 1))
        return band_names


def zonal_stats(grouping, rPath, lPath):
    """ Returns zonal statistics for selected regions

    Returns the mean and standard deviation over selected ROIs with regions
    being grouped by class.

    Args:
        To Do

    Returns:
        To Do
    """

    #First open data and retrieve information
    input_value_raster = rPath
    input_value_shape = lPath
    raster = gdal.Open(input_value_raster)
    shape = ogr.Open(input_value_shape)
    layer = shape.GetLayer()
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(raster.GetProjectionRef())
    pixel_size=30
    transform = raster.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]

    #Initiate the output dictionary
    stats = {}

    #Now do the loop
    for a, b in grouping.iteritems():
        length = len(b)
        _list = tuple(b)
        if len(_list) == 1:
            _list = '(%s)' % ', '.join(map(repr, _list))
        layer.SetAttributeFilter("id = '%d' and FID in %s" % (a, _list))


        #Create temp shapefile
        outShapefile = "tempShape"
        outDriver = ogr.GetDriverByName('MEMORY')

        outDataSource = outDriver.CreateDataSource(outShapefile)
        outLayer = outDataSource.CreateLayer('out', geom_type=ogr.wkbPolygon, srs=raster_srs)
        feat = layer.GetNextFeature()

        # Loop through features for each class, creating one vector
        for f in range(layer.GetFeatureCount()):
            featureDefn = outLayer.GetLayerDefn()
            feature = ogr.Feature(featureDefn)
            geom = feat.GetGeometryRef()
            feature.SetGeometry(geom)
            outLayer.CreateFeature(feat)
            feat = layer.GetNextFeature()
        #outDataSource.Destroy()
        memLayer = outDataSource.GetLayer()

        #Specify offset and rows and columns to read
        xmin, xmax, ymin, ymax = memLayer.GetExtent()
        xoff = int((xmin - xOrigin)/pixelWidth)
        yoff = int((yOrigin - ymax)/pixelWidth)
        xcount = int((xmax - xmin)/pixelWidth)+1
        ycount = int((ymax - ymin)/pixelWidth)+1

        #Create memory target raster
        target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, gdal.GDT_Byte)
        target_ds.SetGeoTransform((
            xmin, pixelWidth, 0,
            ymax, 0, pixelHeight,
        ))

        #Create for target raster the same projection as the valeu raster
        raster_srs = osr.SpatialReference()
        raster_srs.ImportFromWkt(raster.GetProjectionRef())
        target_ds.SetProjection(raster_srs.ExportToWkt())

        # Rasterize zone polygon to raster
        gdal.RasterizeLayer(target_ds, [1], memLayer, burn_values=[1])
         # Read raster as arrays
        #ar.append(nam)
        #create names array
        meani=[]
        stdvi=[]
        for i in range(7):
            i += 1
            banddataraster = raster.GetRasterBand(i)
            dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(np.float)

            bandmask = target_ds.GetRasterBand(1)
            datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(np.float)
         # Mask zone of raster
            zoneraster = np.ma.masked_array(dataraster,  np.logical_not(datamask))

         # Calculate statistics of zonal raster
            value = np.mean(zoneraster)
            valuestdv = np.std(zoneraster)
         #print value

            meani.append(value)
            stdvi.append(valuestdv)
        substats = {}
        substats['std'] = stdvi
        substats['mean'] = meani
        stats[a] = substats
        outDataSource.Destroy()
    return stats

