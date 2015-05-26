# This script will attempt to apply a quadtree based intersection on a list of points.
try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')

def gdal_error_handler(err_class, err_num, err_msg):
    errtype = {
            gdal.CE_None:'None',
            gdal.CE_Debug:'Debug',
            gdal.CE_Warning:'Warning',
            gdal.CE_Failure:'Failure',
            gdal.CE_Fatal:'Fatal'
    }
    err_msg = err_msg.replace('\n',' ')
    err_class = errtype.get(err_class, 'None')
    print 'Error Number: %s' % (err_num)
    print 'Error Type: %s' % (err_class)
    print 'Error Message: %s' % (err_msg)


try:
    import csv, pyqtree
except: 
    sys.exit('Error: cannot find dependent libraries')

from smartquadtree import Quadtree

class Point(object):

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
    
    def __repr__(self):
        return "(%.2f, %.2f) %s" % (self.x, self.y, self.color)
    # The get_x and get_y methods are necessary for the quadtree implementation
    def get_x(self):
        return self.x

    def get_y(self):
        return self.y


'''
Note all callbacks must be decorated either with `@movable_elt` if the coordinates of
any element may have changed, or with `@static_elt` otherwise. The decorator is necessary 
so that the quadtree structure is updated accordingly
'''
from smartquadtree import static_elt
@static_elt
def print_callback(p):
    print p.__repr__()
    #print "[%.2f, %.2f] " % (p[0], p[1])
#q.iterate(print_callback)

ogr.UseExceptions()
wgs = osr.SpatialReference()
wgs.ImportFromEPSG(4326)

# This is the coordinate system used for the plot measurements
# This example uses UTM zone 12N, will need to parameterize this
utm = osr.SpatialReference()
utm.ImportFromEPSG(32612)

yMin = 3.40282e+38
yMax = 1.17549e-38
xMin = 3.40282e+38
xMax = 1.17549e-38
with open('plotnodes.csv', 'rb') as p:
    reader = csv.DictReader(p)
    plots = []
    for row in reader:
        # Create empty polygon geometry for plot
        plot = ogr.Geometry(ogr.wkbPolygon)
        # Create linear ring to add coordinates to
        ring = ogr.Geometry(ogr.wkbLinearRing)
        #print len(row)
        for x in range(1,5):
            #print x
            
            cLon = float(row['X'+`x`])
            if (cLon < xMin): 
              xMin = cLon
            elif (cLon > xMax):
              xMax = cLon
            cLat = float(row['Y'+`x`])
            if (cLat < yMin):
              yMin = cLat
            elif (cLat > yMax):
              yMax = cLat
            coord = (cLon,cLat)
            ring.AddPoint(cLon,cLat)
        plot.AddGeometry(ring)
        #Add plot to list
        plots.append(plot)
        #print plot.GetArea()
    print len(plots)
    print "Min = (%f , %f) Max = (%f, %f)" % (xMin, yMin, xMax, yMax)

'''
initiate Quadtree
'''

q = Quadtree(xMin,yMin,xMax,yMax)
'''
Remove any empty rows or rows missing coordinates
'''
src  =  open('f119_2012_doy201_1pm_cc.csv', 'rb')
tmp = open('cc_tmp.csv', 'wb')
writer = csv.writer(tmp)
for row in csv.reader(src):
    # Remove rows where all fields are empty
    if any(field.strip() for field in row):
       
        writer.writerow(row)
src.close()
tmp.close()

'''
Transform coodinates to UTM so they can be 
compared with the plot coordinates
'''
transform = osr.CoordinateTransformation(wgs, utm)
pointDataSource = ogr.Open("cc.vrt")
lyr = pointDataSource.GetLayer(0)

i = 0;
for feat in lyr:
    geom = feat.GetGeometryRef()
    geom.Transform(transform)
    print "Feature id: %d" % feat.GetFID()
    if (i < 100):
        q.insert([geom.GetX(),geom.GetY()])
        i = i + 1
print "Points projected..."


'''
Add points into quadtree

for feat in lyr:
    geom = feat.GetGeometryRef()
    if (i < 100):
        #geom = feat.GetGeometryRef()

    #    geom = feat.GetGeometryRef()
        #q.insert([geom.GetX(),geom.GetY()],feat.GetFID())
        print i
        i = i + 1
'''        
#q.iterate(print_callback)


''' 
Use the set_mask() method and pass a list of x-y coordinates to filter the iteration process
and apply the function only on elements inside a given polygon. The polygon will be automatically closed.
'''
print plots[0].GetGeometryRef(0).GetPoints(1)
testPlot = plots[0].GetGeometryRef(0).GetPoints(1)

q.set_mask(testPlot)
q.iterate(print_callback)

count = 0
@static_elt
def count_element(p):
    global count
    count += 1
q.iterate(count_element)
print ("%d elements" % count)

'''
Since a mask is set on the quadtree we only counted the elements inside the mask. You can use
the size() method to count elements and ignore the mask by default. Disabling the mask with set_mask(None)
is also a possibility.
'''

print "%d elements (size methods)" % q.size()
print "%d elements (don't ignore the mask)" % q.size(False)

count = 0
q.set_mask(None)
q.iterate(count_element)
print "%d elements (disable the mask)" % count

#%matplotlib inline
from matplotlib import pyplot as plt

@static_elt
def plot_green(p):
    plt.plot([p[0],p[1]], 'o', color='lightgrey')

@static_elt
def plot_red(p):
    plt.plot([p[0], p[1]], 'ro')

fig = plt.figure()
plt.axis([xMin,xMax,yMin,yMax])
q.set_mask(None)
q.iterate(plot_green)
q.set_mask(testPlot)
q.iterate(plot_red)
_ = plt.plot([-3, -3, 3, 3, -3], [-7,7,7,-7,-7], 'r')

fig.show()
