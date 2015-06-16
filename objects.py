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
    def __init__(self, x, y, z):
        #self.x = x
        #self.y = y
        ## Initialize OGR geometry from input coords
        self.geom = ogr.Geometry(ogr.wkbPoint)
        self.geom.AddPoint(x,y,z)
        


    def OffsetGeom(self, offX, offY, offZ,heading):
        ## Offset point using given offset values
        x = self.get_x()
        y = self.get_y()
        z = self.get_z()
        headingRad = heading * math.pi/180.0
        xp = offX * math.cos(-1 * headingRad) - offY * math.sin(-1 * headingRad)
        yp = offX * math.sin(-1 * headingRad) + offY * math.cos(-1 * headingRad)
        zp = offZ + z
        self.geom.AddPoint(x + xp, y + yp, zp)

    def get_x(self): 
        return self.geom.GetX()

    def get_y(self):
        return self.geom.GetY()

    def get_z(self):
        return self.geom.GetZ()

    def get_geom(self):
        return self.geom.ExportToWkt()

class GPS(BasePoint):
    def __init__(self, x, y, z, t):
        self.geom = ogr.Geometry(ogr.wkbPoint)
        self.geom.AddPoint(x,y,z)

    def getDiff(self, leftGPS, rightGPS):
        diffX = (leftGPS.GetX() + rightGPS.GetX()) / 2
        diffY = (leftGPS.GetY() + rightGPS.GetY()) / 2
        diffZ = (leftGPS.GetZ() + rightGPS.GetZ()) / 2
        self.geom.AddPoint(diffX,diffY,diffZ)

    def get_t(self):
        return self.t

class CropCircle(object):
    def __init__(self,t, vi1, vi2, r1, r2, r3):
        self.t = t
        self.vi1 = vi1
        self.vi2 = vi2
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
    
class GreenSeeker(object):
    def __init__(self, t, ndvi, exvi, gsts):
        self.t    = t
        self.ndvi = ndvi
        self.exvi = exvi
        self.gsts = gsts

class InfraTherm(object):
    def __init__(self, t, mV, sbt_c, tt_c):
        self.t  = t
        self.mV = mV
        self.sbt_c = sbt_c
        self.tt_c = tt_c



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

