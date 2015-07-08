
import matplotlib

import numpy as np

import matplotlib.pyplot as plt

import gdal, ogr, osr, numpy, sys, pandas


#Define function to extract mean and std
def get_geometry(grouping):

def proc(fid):

     # Each process needs its own pointer it seems.
    shape = ogr.Open(input_zone_polygon)
    lyr = shape.GetLayer()
    feat = lyr.GetFeature(fid)
    nam = feat.GetField('id')
    raster = gdal.Open(input_value_raster)

     # Get extent of feat
    geom = feat.GetGeometryRef()
    if (geom.GetGeometryName() == 'MULTIPOLYGON'):
        count = 0
        pointsX = []; pointsY = []
        for polygon in geom:
            geomInner = geom.GetGeometryRef(count)
            ring = geomInner.GetGeometryRef(0)
            numpoints = ring.GetPointCount()
            for p in range(numpoints):
                lon, lat, z = ring.GetPoint(p)
                pointsX.append(lon)
                pointsY.append(lat)
            count += 1
    elif (geom.GetGeometryName() == 'POLYGON'):
        ring = geom.GetGeometryRef(0)
        numpoints = ring.GetPointCount()
        pointsX = []; pointsY = []
        for p in range(numpoints):
            lon, lat, z = ring.GetPoint(p)
            pointsX.append(lon)
            pointsY.append(lat)
    xmin = min(pointsX)
    xmax = max(pointsX)
    ymin = min(pointsY)
    ymax = max(pointsY)

     # Specify offset and rows and columns to read
    xoff = int((xmin - xOrigin)/pixelWidth)
    yoff = int((yOrigin - ymax)/pixelWidth)
    xcount = int((xmax - xmin)/pixelWidth)+1
    ycount = int((ymax - ymin)/pixelWidth)+1

     # Create memory target raster
    target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, gdal.GDT_Byte)
    target_ds.SetGeoTransform((
        xmin, pixelWidth, 0,
        ymax, 0, pixelHeight,
    ))

     # Create for target raster the same projection as for the value raster
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(raster.GetProjectionRef())
    target_ds.SetProjection(raster_srs.ExportToWkt())

     # Rasterize zone polygon to raster
    gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])
     # Read raster as arrays
    #ar.append(nam)
    #create names array
    nam = feat.GetField('id')
    names.append(nam)
    meani=[]
    stdvi=[]
    for i in range(7):
        i += 1
        banddataraster = raster.GetRasterBand(i)
        dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)

        bandmask = target_ds.GetRasterBand(1)
        datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(numpy.float)
     # Mask zone of raster
        zoneraster = numpy.ma.masked_array(dataraster,  numpy.logical_not(datamask))

     # Calculate statistics of zonal raster
        value = numpy.mean(zoneraster)
        valuestdv = numpy.std(zoneraster)
     #print value

        meani.append(value)
        stdvi.append(valuestdv)
        #plt.plot(ar)
    return meani, stdvi, names



#Make plot
def plot():
    fig, ax = plt.subplots()
    dtfrm.plot(yerr=dtstd, ax=ax, kind='line')

#Main
def main(vector, raster):
    input_value_raster = raster
    input_zone_polygon = vector
    for i in featList:
        mean, stdv, names=proc(i)
        finmean[i]=mean
        finstdv[i]=stdv
    plot()



#Main Code --> Add to new script
 #Main code

# Raster dataset
input_value_raster = 'raster'


# Vector dataset(zones)
input_zone_polygon = 'ROI.shp'


# Open data
rast = gdal.Open(input_value_raster)
shp = ogr.Open(input_zone_polygon)


# Get raster georeference info
transform = rast.GetGeoTransform()
xOrigin = transform[0]
yOrigin = transform[3]
pixelWidth = transform[1]
pixelHeight = transform[5]


layer = shp.GetLayer()
featList = range(layer.GetFeatureCount())
finmean=np.zeros((layer.GetFeatureCount(),7))
finstdv=np.zeros((layer.GetFeatureCount(),7))

#setup names array
names=[]
arr=[]
mean=[]
stdv=[]

main()

#Turn into dataframe with header
dtfrm=pandas.DataFrame(data=np.transpose(finmean),columns=names)
dtstd=pandas.DataFrame(data=np.transpose(finstdv),columns=names)

