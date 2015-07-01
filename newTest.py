import ogr
import parse
from smartquadtree import Quadtree


centroidExtent = parse.getCentroidExtent("plots.shp")
centroid = centroidExtent[0]
width = centroidExtent[1]
height = centroidExtent[2]

q = Quadtree(centroid.get_x(), centroid.get_y(), width, height)
# set 1 meter limit on quadtree leaves
q.set_limitation(1)


