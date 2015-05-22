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
        print len(row)
        for x in range(1,5):
            print x
            
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
        print plot.GetArea()
    print len(plots)
    print "Min = (%f , %f) Max = (%f, %f)" % (xMin, yMin, xMax, yMax)

#create a quad tree based on plot bounds

#xMin = -131.35
#yMin = 38
#xMax = 10.1687
#yMax = 56

spindex = pyqtree.Index(bbox=[xMin,yMin,xMax,yMax])

src  =  open('f119_2012_doy201_1pm_cc.csv', 'rb')
tmp = open('cc_tmp.csv', 'wb')
writer = csv.writer(tmp)
for row in csv.reader(src):
    # Remove rows where all fields are empty
    if any(field.strip() for field in row):
       
        writer.writerow(row)
src.close()
tmp.close()


transform = osr.CoordinateTransformation(wgs, utm)
pointDataSource = ogr.Open("cc.vrt")
print pointDataSource.__len__()
lyr = pointDataSource.GetLayer(0)
#print lyr
i = 0
for feat in lyr:
    if (i < 100):
        geom = feat.GetGeometryRef()
        geom.Transform(transform)
        print "Feature id: %d" % feat.GetFID()
        print geom.ExportToWkt()
     
        #print feat.__getitem__('SENSOR')
        spindex.insert(item=geom, bbox=geom.GetEnvelope())
        i = i + 1
    
print "Total points is: %d "  % spindex.countmembers()

#print spindex.bbox
#for i in plots:
  #print i.GetEnvelope()

  #plotMatches = spindex.intersect(i.GetEnvelope())
  #print `len(plotMatches)`
