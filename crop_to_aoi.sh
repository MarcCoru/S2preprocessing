#!/bin/bash

# wrapper around warp.sh and vrap via vrt
#
# if wrap.sh fails with L2A Sentinel 2 images. Crop images via VRTs

# read configs
. $1

# either L1C or L2A
level=$2

gdalwarp=conda/bin/gdalwarp

if [ "$level" = "L1C" ]; then
    gdalS2prefix="SENTINEL2_L1C"
elif [ "$level" = "L2A" ]; then
    gdalS2prefix="SENTINEL2_L2A"
else
    echo "please specify level ('L1C' or 'L2A') as second argument"
    echo "e.g. \$sh warp.sh demo.cfg L1C"
    exit 0
fi
#statements

# default output directory to path if not defined
if [ -z "$tifpath" ]; then
    tifpath=$path
fi

#bash warp.sh $1 $2 &> warp.log

# catch products which have caused ERROR 6
products=$(grep -B1 "ERROR 6" warp.log | grep S2)


for product in $products
do
  # create VRTs
  python addvrttoproduct.py $path/$product.SAFE --bandconfigfile cfg/bandsvrtsequence.json --gdalbuildvrt conda/bin/gdalbuildvrt

  # replace _ with : e.g. EPSG_32632 -> EPSG:32632
  t_srs=$(echo $srs | sed 's/_/:/g')

  # create clips
  echo $path/$product
  $gdalwarp -t_srs $t_srs -of GTiff -crop_to_cutline -cutline $cutline $path/$product.SAFE/10m.vrt "$tifpath/$product"_10m.tif
  $gdalwarp -t_srs $t_srs -of GTiff -crop_to_cutline -cutline $cutline $path/$product.SAFE/20m.vrt "$tifpath/$product"_20m.tif
  $gdalwarp -t_srs $t_srs -of GTiff -crop_to_cutline -cutline $cutline $path/$product.SAFE/60m.vrt "$tifpath/$product"_60m.tif

done
