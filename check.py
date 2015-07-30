import sqlite3
import parse

print "Updating records"
parse.projGNSS('+proj=utm +zone=12 +datum=WGS84 +units=m +no_defs')
#parse.updateClosestGNSS()
#print "Checking updates"
#parse.selectCCData()
