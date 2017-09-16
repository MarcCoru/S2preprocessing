#!/bin/bash

cfg_path=$1

sh query.sh $cfg_path
sh download.sh $cfg_path

sh warp.sh $cfg_path L1C


# create a 3.84 km tile grid 60m * 2 ** 6
python grid.py sites/bavaria.site sites/bavaria.geojson gridtraintest --tilesize 3840 --margin 0

# add eval t/f field to tile grid
bash addEvalField.sh sites/bavaria.site gridtraintest eval 0.8 ""

# add train/valid field for fold 0 if eval is not true
for fold in 0 1 2 3 4 5 6 7 8 9
do
    bash addEvalField.sh sites/bavaria.site gridtraintest train$fold 0.75 "where eval = 'f'"
done

# create grids for sample tiles:
for tilesize in 60 120 240 480
do
    python grid.py sites/bavaria.site sites/bavaria.geojson tiles$tilesize --tilesize $tilesize
done
