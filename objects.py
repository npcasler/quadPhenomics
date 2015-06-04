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
        print self.geom.GetPointCount()
        ## Return the cooordinates from the external ring(boundary) using only 2d coordinates
        return self.geom.GetBoundary().GetPoints(2)

