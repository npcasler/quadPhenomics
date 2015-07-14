import os, sys

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

try:
    from smartquadtree import Quadtree, static_elt
except:
    sys.exit('ERROR: cannot find quadtree modules')

try: 
    from datetime import datetime
except: 
    sys.exit('ERROR: cannot load date/time modules')


try:
    import calendar
except:
    sys.exit('ERROR: trouble loading calendar module')

try: 
    import sqlite3
except: 
    sys.exit('ERROR: could not load sqlite module')

try:
    import pyproj
except:
    sys.exit('ERROR: could not load pyproj module')

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

def openConnect():
    conn = sqlite3.connect('test.db')
    return conn

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
    point = BasePoint(feature.GetFID(), geom.GetX(), geom.GetY())
    return point

# param shapefile: path to shapefile to open
def readShape(shapefile):
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shapefile, 0) # 0 signifies read-only, 1 is writeable
    print dataSource
    # Check if shapefile is found
    if dataSource is None:
        print 'Could not open %s' % (shapefile)
    else:
        print 'Opened %s' % shapefile
        layer = dataSource.GetLayer(0)
        print "Layer has %d features" % layer.GetFeatureCount()
        layerDefinition = layer.GetLayerDefn()
        extent = layer.GetExtent()
        print extent
        shape = layer    

    dataSource.Destroy()
    return shape

def createTable():
    conn = openConnect()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS sensor(id integer, x float, y float, plot_id text)")
    conn.commit()
    conn.close()

def createGNSSTable():
    conn = openConnect()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS gnss(id integer primary key autoincrement, tstamp float, long float, lat float, heading float, elev float)")
    conn.commit()
    conn.close()

def addGNSSIndex():
    conn = openConnect()
    c = conn.cursor()
    c.execute("CREATE INDEX gTstamp ON gnss (tstamp)")
    conn.commit()
    conn.close()

def createCCTable():
    conn = openConnect()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS crop_circle(id integer primary key autoincrement, sens_id text, tstamp float, c1 float, c2 float, c3 float, vi1 float, vi2 float, gnss_id integer)")
    conn.commit()
    conn.close()

def updateClosestGNSS():
    conn = openConnect()
    c = conn.cursor()
    #c.execute("SELECT a.id, a.sens_id, a.tstamp as astamp, b.tstamp as bstamp, b.lat, b.long,  FROM crop_circle AS a, (SELECT * FROM crop_circle c ,gnss d WHERE d.tstamp < c.tstamp ORDER BY d.tstamp DESC LIMIT 1) AS b")
    #c.execute("SELECT a.id, a.tstamp, (SELECT b.id FROM gnss b WHERE b.tstamp < a.tstamp ORDER BY b.tstamp DESC LIMIT 1) AS gid FROM crop_circle a")
    c.execute("UPDATE crop_circle SET gnss_id = (SELECT id FROM gnss AS b WHERE b.tstamp < crop_circle.tstamp ORDER BY b.tstamp DESC LIMIT 1)")

    print "Fetching records"
    #print c.fetchone()
    conn.commit()
    #yield p
    conn.close()

def selectCCData():
    conn = openConnect()
    c = conn.cursor()
    c.execute("SELECT a.*, b.lat, b.long, b.elev FROM crop_circle a, gnss b WHERE a.gnss_id = b.id LIMIT 10")
    p = c.fetchall()
    print p
    conn.commit()
    conn.close()

def checkPoints(q, plot_id):
    global pointList
     
    pointList = []
    @static_elt
    def print_point(p):
        global pointList
        
        #if p.get_id() is None:
        #    return
        pointInfo = (p.get_id(), p.get_x(), p.get_y(), plot_id)
        pointList.append(pointInfo)
    q.iterate(print_point)
    print pointList
    return pointList



def insertPoints(pointList):
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.executemany("INSERT INTO sensor(id,x,y,plot_id) VALUES (?, ?, ?, ?)", pointList)
    conn.commit()
    conn.close()
    
def insertGNSS(gnssLog):
    conn = openConnect()
    c = conn.cursor()
    with open(gnssLog, 'rb') as gLog:
        dr = csv.DictReader(gLog)
        to_db = [(i['utc_tstamp'], i['latitude'],i['longitude'], i['heading'], i['elevation']) for i in dr]
    c.executemany("INSERT INTO gnss(tstamp,lat,long,heading,elev) VALUES (?, ?, ?, ?, ?)", to_db)
    conn.commit()
    conn.close()

def insertCC(ccLog):
    conn = openConnect()
    c = conn.cursor()
    with open(ccLog, 'rb') as cLog:
        dr = csv.DictReader(cLog)
        to_db = [(i['sensor_ID'], i['utc_tstamp'], i['channel_1'], i['channel_2'], i['channel_3'], i['vi_1'],i['vi_2']) for i in dr]
        c.executemany("INSERT INTO crop_circle(sens_id,tstamp,c1,c2,c3,vi1,vi2) VALUES (?, ?, ?, ?, ?, ?, ?)", to_db)
    conn.commit()
    conn.close()

def outputPoints(outFile):
    if outFile == "" or outFile is None:
        sys.exit("ERROR: No output file specified")
    conn = openConnect()
    c = conn.cursor()
    p = c.execute("SELECT * FROM sensor")
    with open(outFile, "wb") as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write headers
        csv_writer.writerow([i[0] for i in c.description])
        # Write data
        csv_writer.writerows(c)
    

def selectPoints():
    conn = openConnect()
    c = conn.cursor()
    p = c.execute("SELECT * FROM sensor")
    conn.commit()
    print p
    conn.close()

def clearTable(table):
    conn = openConnect()
    c = conn.cursor()
    
    c.execute("DELETE FROM "+  table)
    #p = c.execute("DELETE FROM ?", (table))
    conn.commit()
    conn.close()

def setQtreeMask(maskShapefile, quadtree):
    driver =  ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(maskShapefile, 0)
    q = quadtree

    if dataSource is None:
        print 'Could not open %s' % (maskShapefile)
    else: 
        print 'Opened %s' % maskShapefile
        layer = dataSource.GetLayer(0)
        q.set_mask(None)
        intersects = [];
        for feature in layer:
            plot_id = feature.GetField("plot_id")
            intersect = []
            
            
            geom = feature.GetGeometryRef().GetBoundary().GetPoints(2)
            q.set_mask(geom)
            print geom
            print "%d elements (don't ignore the mask)" % q.size(False)
            p = checkPoints(q, plot_id)
            intersects.extend(p)
            
            q.set_mask(None)
        print intersects
        insertPoints(intersects)
    dataSource.Destroy()




def getExtentFromShape(shapefile):
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shapefile, 0) # 0 signifies read-only, 1 is writeable
    print dataSource
    # Check if shapefile is found
    if dataSource is None:
        print 'Could not open %s' % (shapefile)
    else:
        print 'Opened %s' % shapefile
        layer = dataSource.GetLayer(0)
        layerDefinition = layer.GetLayerDefn()
        extent = layer.GetExtent()
        return extent
        

    dataSource.Destroy()


def getCentroidExtent(shapefile):
    extent = getExtentFromShape(shapefile)
    width = extent[1] - extent[0]
    height = extent[3] - extent[2]
    centroidX = extent[0] + width/2
    centroidY = extent[2] + height/2
    centroid = BasePoint(9999, centroidX,centroidY)
    centroidExtent = [centroid, width, height]
    return centroidExtent


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


def iso8601_to_epoch(datestring):
    """ 
    This function copied from https://gist.github.com/squioc/3078803
    iso8601_to_epoch - convert the iso8601 date into the unix epoch time

    > iso8601_to_epoch("2012-07-09T22:27:50.272517")
    1341872870
    """
    return calendar.timegm(datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%S.%f").timetuple())



def writePlotShapefile(plots):
    #set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")

    wgs = osr.SpatialReference()
    wgs.ImportFromEPSG(4326)

    # This is the coordinate system used for the plot measurements
    # This example uses UTM zone 12N, will need to parameterize this
    utm = osr.SpatialReference()
    utm.ImportFromEPSG(32612)
    
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
