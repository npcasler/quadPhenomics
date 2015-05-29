try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')
try: 
    import math
except: 
    sys.exit('ERROR: cannot find Math module')

try: 
    import csv
except:
    sys.exit('ERROR: cannot find CSV module')

try: 
    from smartquadtree import Quadtree, static_elt
except:
    sys.exit('ERROR: cannot find Quadtree module')

class BasePoint(object):
    def __init__(self, x, y):
        #self.x = x
        #self.y = y
        ## Initialize OGR geometry from input coords
        self.geom = ogr.Geometry(ogr.wkbPoint)
        self.geom.AddPoint(x,y)
        


    def OffsetGeom(self, offX, offY, heading):
        ## Offset point using given offset values
        x = self.get_x()
        y = self.get_y()
        headingRad = heading * math.pi/180.0
        xp = offX * math.cos(-1 * headingRad) - offY * math.sin(-1 * headingRad)
        yp = offX * math.sin(-1 * headingRad) + offY * math.cos(-1 * headingRad)
        self.geom.AddPoint(x + xp, y + yp)

    def get_x(self): 
        return self.geom.GetX()

    def get_y(self):
        return self.geom.GetY()

    def get_geom(self):
        return self.geom.ExportToWkt()


class Plot(object):
    def __init__(self,barcode):
        self.barcode = barcode
        self.geom = ogr.Geometry(ogr.wkbPolygon)

    
    def get_barcode(self):
        return self.barcode
    
    def get_geom(self):
        return self.geom.GetGeometryName()
        #return self.geom.GetBoundary()
    
    def get_points(self):
        self.geom.CloseRings()
        print self.geom.GetPointCount()
        return self.geom.GetPoints()

## Initiate the projections
wgs = osr.SpatialReference()
wgs.ImportFromEPSG(4326)

## Initiate the UTM projection
utm = osr.SpatialReference()
utm.ImportFromEPSG(32612)

testX = 409117.50416
testY = 3659517.08689
heading = 268.70999
offX = -1.524
offY = 0.130175

p = BasePoint(testX,testY)

print p.get_x()
print p.get_y()
print p.get_geom()
p.OffsetGeom(offX, offY, heading)
print p.get_geom()
