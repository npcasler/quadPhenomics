## Load a file

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
    from shapely.geometry import Point, Polygon
except: 
    sys.exit('Error: cannot find dependent libraries')

if __name__ == '__main__':
    # install error handler
    gdal.PushErrorHandler(gdal_error_handler)



ogr.UseExceptions()

xMin = -131.35
yMin = 38
xMax = 10.1687
yMax = 56

spindex = pyqtree.Index(bbox=[xMin,yMin,xMax,yMax])

overlapBbox = (-129,44,-118,48.31)

wgs = osr.SpatialReference()
wgs.ImportFromEPSG(4326)

# This is the coordinate system used for the plot measurements
# This example uses UTM zone 12N, will need to parameterize this
utm = osr.SpatialReference()
utm.ImportFromEPSG(32612)

transform = osr.CoordinateTransformation(wgs, utm)

with open('plotnodes.csv', 'rb') as p:
    reader = csv.DictReader(p)
    plots = []
    for row in reader:
        plot = []
        for x in range(1,5):
            print x
            cLon = float(row['X'+`x`])
            cLat = float(row['Y'+`x`])
            coord = (cLon,cLat)
            print(coord)
            plot.append(coord)
        plotPoly = Polygon(plot)
        plots.append(plotPoly)
    print plots[5]

src  =  open('f119_2012_doy201_1pm_cc.csv', 'rb')
tmp = open('cc_tmp.csv', 'wb')
writer = csv.writer(tmp)
for row in csv.reader(src):
    # Remove rows where all fields are empty
    if any(field.strip() for field in row):
       
        writer.writerow(row)
src.close()
tmp.close()




pointDataSource = ogr.Open("cc.vrt")
print pointDataSource.__len__()
lyr = pointDataSource.GetLayer(0)
#print lyr
for feat in lyr:
    geom = feat.GetGeometryRef()
    geom.Transform(transform)
    print feat
    print geom.ExportToWkt()
     
'''
with open('f119_2012_doy201_1pm_cc.csv', 'rb') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print row['LONGITUDE']
        xLon = row['LONGITUDE']
        xLat = row['LATITUDE']
        # Check for null coordinates
        if bool(xLon.strip()) and bool(xLat.strip()):

            point = Point(float(xLon), float(xLat))
            geom = ogr.CreateGeometryFromWkb(point.wkb)
            geom.Transform(transform)
            print geom.GetEnvelope
            spindex.insert(item=geom, bbox=geom.GetEnvelope())
        else: 
            print "Coordinates missing"
    
    matches = spindex.intersect(overlapBbox)
    for i in plots:
        plotMatches = spindex.intersect(i.bounds)
        print `i` + `len(plotMatches)`
   ''' 
