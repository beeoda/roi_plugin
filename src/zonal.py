""" Code for extracting polygon summary statistics from a raster

For reference see:
http://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html#calculate-zonal-statistics
"""
from osgeo import gdal, ogr, osr
import numpy as np

gdal.AllRegister()
gdal.UseExceptions()


def zonal_stats(grouping, vlayer, rlayer):
    """ Returns zonal statistics for selected regions

    Returns the mean and standard deviation over selected ROIs with regions
    being grouped by class.

    Args:
      grouping (dict): dict containing lists of FIDs organized by user defined
        aggregation (d[grouping] = [fids])
      vlayer (QgsVectorLayer): Vector layer of polygons used for location of
        statistic retrievals
      rlayer (QgsRasterLayer): Raster layer of data containing data to extract
        from

    Returns:
      dict: dict of dicts of statistics including mean and standard deviation
        (e.g., d[class].keys() = ['mean', 'std'])

    """
    # First open data and retrieve information
    raster_ds = gdal.Open(rlayer.source())
    vector_ds = ogr.Open(vlayer.source())
    layer = vector_ds.GetLayer()

    # Get spatial reference systems & setup coordinate transformation
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(raster_ds.GetProjectionRef())
    vector_srs = layer.GetSpatialRef()

    coord_trans = osr.CoordinateTransformation(vector_srs, raster_srs)

    gt = raster_ds.GetGeoTransform()
    ul_x, ul_y = gt[0], gt[3]
    ps_x, ps_y = gt[1], gt[5]

    # Initiate the output dictionary
    stats = {}
    # for a, b in grouping.iteritems():
    for k, val in grouping.iteritems():
        layer.SetAttributeFilter('FID in ({fid})'.format(
            fid=','.join(map(str, val))))

        driver = ogr.GetDriverByName('MEMORY')
        out_ds = driver.CreateDataSource('tmp')
        out_layer = out_ds.CreateLayer(
            'out', geom_type=ogr.wkbPolygon, srs=raster_srs)
        feat = layer.GetNextFeature()

        # Loop through features for each class, creating one vector
        for f in range(layer.GetFeatureCount()):
            featureDefn = out_layer.GetLayerDefn()
            feature = ogr.Feature(featureDefn)
            geom = feat.GetGeometryRef()
            geom.Transform(coord_trans)

            feature.SetGeometry(geom)
            out_layer.CreateFeature(feat)
            feat = layer.GetNextFeature()

        memLayer = out_ds.GetLayer()

        # Specify offset and rows and columns to read
        xmin, xmax, ymin, ymax = memLayer.GetExtent()
        xoff = int((xmin - ul_x) / ps_x)
        yoff = int((ul_y - ymax) / ps_x)
        xcount = int((xmax - xmin) / ps_x) + 1
        ycount = int((ymax - ymin) / ps_x) + 1

        # Create memory target raster
        target_ds = gdal.GetDriverByName('MEM').Create(
            '', xcount, ycount, gdal.GDT_Byte)
        target_ds.SetGeoTransform((xmin, ps_x, 0,
                                   ymax, 0, ps_y))

        # Create for target raster the same projection as the valeu raster
        raster_srs = osr.SpatialReference()
        raster_srs.ImportFromWkt(raster_ds.GetProjectionRef())
        target_ds.SetProjection(raster_srs.ExportToWkt())

        # Rasterize zone polygon to raster
        status = gdal.RasterizeLayer(target_ds, [1], memLayer, burn_values=[1])
        if status != 0:
            raise Exception('Failed to rasterize features in group {}'.format(
                g=k))

        # Read raster as arrays
        meani = []
        stdvi = []
        for i in range(raster_ds.RasterCount):
            band = raster_ds.GetRasterBand(i + 1)
            data = band.ReadAsArray(
                xoff, yoff, xcount, ycount).astype(np.float)

            mask = target_ds.GetRasterBand(1)
            mask = mask.ReadAsArray(0, 0, xcount, ycount).astype(np.float)

            # Mask zone of raster
            zoneraster = np.ma.masked_array(data, np.logical_not(mask))

            # Calculate statistics of zonal raster
            meani.append(np.mean(zoneraster))
            stdvi.append(np.std(zoneraster))

        substats = {}
        substats['std'] = np.asarray(stdvi)
        substats['mean'] = np.asarray(meani)
        stats[k] = substats
        out_ds.Destroy()

    return stats
