import sys

try: 
    import csv
except:
    sys.exit('ERROR: cannot find CSV modules')

try: 
    from osgeo import ogr, osr
except:
    sys.exit('ERROR: cannot find osgeo modules')
try: 
    from objects import BasePoint, Plot
except:
    sys.exit('ERROR: cannot find object definitions')


'''
Remove any empty rows or rows missing coordinates

src  =  open('f119_2012_doy201_1pm_cc.csv', 'rb')
tmp = open('cc_tmp.csv', 'wb')
writer = csv.writer(tmp)
for row in csv.reader(src):
    # Remove rows where all fields are empty
    if any(field.strip() for field in row):

        writer.writerow(row)
src.close()
tmp.close()


Transform coodinates to UTM so they can be 
compared with the plot coordinates


pointDataSource = ogr.Open("cc.vrt")
lyr = pointDataSource.GetLayer(0)
#lyr.SetSpatialFilter(plots[0].geom)
for feat in lyr:
    geom = feat.GetGeometryRef()
    geom.Transform(transform)
    point = BasePoint(geom.GetX(), geom.GetY())
    #print point.get_geom()
    #print "Feature id: %d" % feat.GetFID()
    q.insert(point)
'''    

def cleanCSV(inputCSV, outputCSV):
    src = open(inputCSV, 'rb')
    tmp = open(outputCSV, 'wb')
    writer = csv.writer(tmp)
    for row in csv.reader(src):
        # Remove rows where all fields are empty
        if any(field.strip() for field in row):
            writer.writerow(row)
    src.close()
    tmp.close()

def projectPoint(feature):
    wgs = osr.SpatialReference()
    wgs.ImportFromEPSG(4326)

    # This is the coordinate system used for the plot measurements
    # This example uses UTM zone 12N, will need to parameterize this
    utm = osr.SpatialReference()
    utm.ImportFromEPSG(32612)

    transform = osr.CoordinateTransformation(wgs, utm)

    geom = feature.GetGeometryRef()
    geom.Transform(transform)
    point = BasePoint(geom.GetX(), geom.GetY())
    return point


def createPlots(filename):


    yMin = 3.40282e+38
    yMax = 1.17549e-38
    xMin = 3.40282e+38
    xMax = 1.17549e-38
    with open(str(filename), 'rb') as p:
        reader = csv.DictReader(p)
        plots = []
        for row in reader:
            # Create empty polygon geometry for plot
            plot = Plot(row['BARCODE']) 
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

            ring.CloseRings()
            plot.geom.AddGeometry(ring)
            #Add plot to list
            plots.append(plot)
            #print plot.geom.GetArea()
        #print len(plots)
        print "Min = (%f , %f) Max = (%f, %f)" % (xMin, yMin, xMax, yMax)
        plotInfo = {'plots': plots, 'xMin': xMin, 'yMin': yMin, 'xMax': xMax, 'yMax': yMax}
    return plotInfo

