#!/bin/bash

for i in {2..136}; do
echo $(date +"%d.%m.%Y %H:%M:%S") idx $i
psql -d fields -c "drop index if exists bavaria_st_convexhull_idx$i";
done
