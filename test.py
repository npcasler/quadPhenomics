# This script will attempt to apply a quadtree based intersection on a list of points.
import sys
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


plotInfo = parse.createPlots('plotnodes.csv')
#print plotInfo
width = plotInfo['xMax'] - plotInfo['xMin']
print "WIDTH = %f" % width
height = plotInfo['yMax'] - plotInfo['yMin']
print "HEIGHT = %f" % height
centroid = BasePoint(plotInfo['xMin'] + width/2,plotInfo['yMin'] + height/2)
print "Centroid = %f , %f" % (centroid.get_x(), centroid.get_y())

plots = plotInfo['plots']

def writePlotShapefile(plots):
    #set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")

    # create the data source
    data_source = driver.CreateDataSource("plots.shp")

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
