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
try: 
    import sqlite3
except:
    sys.exit('Error cannot find sqlite module')
try:
    import getopt
except:
    sys.exit('ERROR: cannot load getopt module')


'''
Note all callbacks must be decorated either with `@movable_elt` if the coordinates of
any element may have changed, or with `@static_elt` otherwise. The decorator is necessary 
so that the quadtree structure is updated accordingly
'''
from smartquadtree import static_elt


def main(argv):
    print argv
    inputfile = ''
    gnssLog = ''
    sensorLog = ''
    plotFile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:g:s:p:o:",["inFile=","gnssLog=","sensorLog=","plotFile=","outFile="])
    except getopt.GetoptError:
        print 'test.py -i <inputfile> -g <gnssLog> -s <sensorLog> -p <plotFile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputfile> -g <gnssLog> -s <sensorLog> -p <plotFile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--inFile"):
            inputfile = arg
        elif opt in ("-o", "--outFile"):
            outputfile = arg
        elif opt in ("-p", "--plotFile"):
            plotFile = arg
        elif opt in ("-g", "--gnssLog"):
            gnssLog = arg
        elif opt in ("-s", "--sensorLog"):
            sensorLog = arg
    print 'Input File is ', inputfile
    print 'GNSS Log is ', gnssLog
    print 'Sensor Log is ', sensorLog
    print 'Output File is ', outputfile
    print 'Plot File is ', plotFile
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

    plots = parse.readShape(plotFile)
    extent = parse.getCentroidExtent(plotFile)
    print "Extent is"
    print extent
    #plots = plotInfo['plots']




    print "Initiating Quadtree"
    
    #q = Quadtree(centroid.get_x(),centroid.get_y(),width,height)
    q = Quadtree(extent[0].get_x(), extent[0].get_y(),extent[1],extent[2])
    q.set_limitation(5)

    parse.cleanCSV(inputfile, 'cc_tmp.csv')

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
    TESTING QUADTREE INTERSECT
    '''

    #writePlotShapefile(plots)

    '''count = 0
    print "ID,x,y"
    for feat in lyr:
        geom = feat.GetGeometryRef()
        #print feat.GetFID()
        point = BasePoint(feat.GetFID(), geom.GetX(), geom.GetY())
        print "%d, %f, %f" % (feat.GetFID(), geom.GetX(), geom.GetY())
        count += 1
        q.insert(point)
    print "%d Points inserted into Quadtree" % count
    print "%d element inside quadtree" % q.size()
      '''
        
        
        
    
    #parse.createTable()
    parse.createGNSSTable()
    parse.createCCTable()
    parse.clearTable("gnss")
    parse.clearTable("crop_circle")
    parse.insertGNSS(gnssLog)
    parse.addGNSSIndex()
    # Insert the crop circle data
    parse.insertCC(sensorLog) 
    # Add gnss foreign keys based on timestamp
    parse.updateClosestGNSS()

    parse.selectCCData()
    srs = parse.getProj(plotFile)
    print srs
    test = parse.projectCoords(-96.6191598,39.1328326,110,srs)
    print test
    parse.projGNSS(srs)
    #parse.setQtreeMask(plotFile, q)
    #parse.outputPoints(outputfile)


    '''
    #q.iterate(print_callback)


    Use the set_mask() method and pass a list of x-y coordinates to filter the iteration process
    and apply the function only on elements inside a given polygon. The polygon will be automatically closed.
    '''

if __name__ == "__main__":
    main(sys.argv[1:])
