""" Miscellaneous utility functions for plugin use
"""
import re

from osgeo import gdal


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
    # Abbreviate lingering "reflecance"
    name = re.sub('(?i)refl[a-z]*', 'refl', name)
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
