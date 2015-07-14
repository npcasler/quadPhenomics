import sqlite3
import parse

print "Updating records"
parse.updateClosestGNSS()
print "Checking updates"
parse.selectCCData()
