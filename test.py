# This script will attempt to apply a quadtree based intersection on a list of points.
import os, sys
try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')
try: 
    import csv
except: 
    sys.exit('ERROR: cannot find CSV modules')
try:
    import parse
except:
    sys.exit('ERROR: cannot find parse module')
try: 
    from objects import BasePoint, Plot
except: 
    sys.exit('ERROR: cannot find object definitions')

try:
    from smartquadtree import Quadtree, static_elt
except:
    sys.exit('ERROR: cannot find Quadtree module')



'''
Note all callbacks must be decorated either with `@movable_elt` if the coordinates of
any element may have changed, or with `@static_elt` otherwise. The decorator is necessary 
so that the quadtree structure is updated accordingly
'''
from smartquadtree import static_elt

ogr.UseExceptions()
wgs = osr.SpatialReference()
wgs.ImportFromEPSG(4326)

# This is the coordinate system used for the plot measurements
# This example uses UTM zone 12N, will need to parameterize this
utm = osr.SpatialReference()
utm.ImportFromEPSG(32612)


#plotInfo = parse.createPlots('plotnodes.csv')
#print plotInfo
#width = plotInfo['xMax'] - plotInfo['xMin']
#print "WIDTH = %f" % width
#height = plotInfo['yMax'] - plotInfo['yMin']
#print "HEIGHT = %f" % height
#centroid = BasePoint(plotInfo['xMin'] + width/2,plotInfo['yMin'] + height/2)
#print "Centroid = %f , %f" % (centroid.get_x(), centroid.get_y())

plots = parse.readShape("plots.shp")
extent = parse.getExtentFromShape("plots.shp")
#plots = plotInfo['plots']

def writePlotShapefile(plots):
    #set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")

    # create the data source
    if os.path.exists('plots.shp'):
        driver.DeleteDataSource('plots.shp')
    data_source = driver.CreateDataSource("plots.shp")

    # create spatial reference
    srs = utm

    # Create the layer
    layer = data_source.CreateLayer("plots", srs, ogr.wkbPolygon)

    # Add the fields we're interested in
    field_plot_id = ogr.FieldDefn("plot_id", ogr.OFTString)
    field_plot_id.SetWidth(24)
    layer.CreateField(field_plot_id)

    for plot in plots:
        # create the feature
        feature = ogr.Feature(layer.GetLayerDefn())
        # set the feature attributes
        feature.SetField("plot_id", plot.plot_id)
        print "Plot barcode: %s" % plot.plot_id
        print "Geometry: %s" % plot.get_geom()
        # set the feature geometry
        feature.SetGeometry(plot.get_geom())
        #create the feature in the layer(shapefile)
        layer.CreateFeature(feature)
        # Destroy the feature to free resources
        feature.Destroy()
    # Destroy the data source to free resources
    data_source.Destroy()

@static_elt
def print_points(p):
    print "HELLO"
    print "[%f, %f]" % p.get_x(), p.get_y()

'''
initiate Quadtree
'''
q = Quadtree(centroid.get_x(),centroid.get_y(),width,height)
q.set_limitation(1)

parse.cleanCSV('f119_2012_doy201_1pm_cc.csv', 'cc_tmp.csv')

'''
Add points into quadtree
'''


'''Comment out for benchmarking 
pointDataSource = ogr.Open('cc.vrt')
lyr = pointDataSource.GetLayer(0)

print "Adding points to Quadtree"
for feat in lyr:
    point = parse.projectPoint(feat)
    q.insert(point)

print "Points projected..."
for plot in plots:
    q.set_mask(plot.get_points())
    print "%d elements (don't ignore the mask)" % q.size(False)
    q.set_mask(None)

'''

pointDataSource = ogr.Open('cc-proj.vrt')
lyr = pointDataSource.GetLayer(0)
'''
TESTING SIMPLE INTERSECT
'''
'''
print "Filtering features"
for plot in plots:
    lyr.SetSpatialFilter(plot.geom)
    count = 0
    for feature in lyr:
        count = count + 1
        print count
'''
'''
TESTING QUADTREE INTERSECT
'''

writePlotShapefile(plots)


for feat in lyr:
    geom = feat.GetGeometryRef()
    point = BasePoint(geom.GetX(), geom.GetY())
    q.insert(point)
  
for plot in plots:
    q.set_mask(plot.get_points())
    #print "%d elements (don't ignore the mask)" % q.size(False)
    q.set_mask(None)



'''
#q.iterate(print_callback)


Use the set_mask() method and pass a list of x-y coordinates to filter the iteration process
and apply the function only on elements inside a given polygon. The polygon will be automatically closed.
'''
