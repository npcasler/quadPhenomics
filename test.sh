#!/bin/bash

# Test for quadtree implementation
> outcsv.csv
> outLog
rm test.db

python test.py -i docs/f119_2012_doy201_1pm_cc.csv -o outcsv.csv

echo "Number of points output from quadtree is "
cat outcsv.csv | wc -l
