## Load a file

import csv, pyqtree
from shapely.geometry import Point, Polygon



xMin = -131.35
yMin = 38
xMax = 10.1687
yMax = 56

spindex = pyqtree.Index(bbox=[xMin,yMin,xMax,yMax])

overlapBbox = (-129,44,-118,48.31)

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


            

with open('Abies_amabilis.csv', 'rb') as f:
    reader = csv.DictReader(f)
    for row in reader:
        point = Point(float(row['longitude']), float(row['latitude']))
        #print point.bounds
        spindex.insert(item=point, bbox=point.bounds)
    
    matches = spindex.intersect(overlapBbox)
    for i in plots:
        plotMatches = spindex.intersect(i.bounds)
        print `i` + `len(plotMatches)`
    print len(matches)
