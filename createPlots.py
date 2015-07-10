import os, sys

try: 
    from osgeo import ogr, osr, gdal
except: 
    sys.exit('ERROR: cannot find GDAL/OGR modules')

try:
    import parse
except:
    sys.exit('ERROR: cannot find parse module')

plotInfo = parse.createPlots('plotnodes.csv')

plots = plotInfo['plots']

parse.writePlotShapefile(plots)
