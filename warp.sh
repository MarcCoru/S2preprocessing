#!/bin/bash

# read configs
. $1

# either L1C or L2A
level=$2

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

# should be installed there by setup.sh
gdalwarp="conda/bin/gdalwarp"

# for every line in the results file $path/results.txt
while read p;
do

    # select product name
    if [ "$level" = "L1C" ]; then
        product=$p
    elif [ "$level" = "L2A" ]; then
        # predict L2A product name
        product=$(echo $p | sed 's/MSIL1C/MSIL2A/g' | sed 's/OPER/USER/g' )
    fi

    echo $product

    # find product's main xml file:
    #  -> list directory filter by regex, return first match
    file=$(ls $path/$product.SAFE | grep -E -m 1 "(S2.*xml|MTD.*xml)")

    $gdalwarp -of GTiff -crop_to_cutline -cutline $cutline "$gdalS2prefix:$path/$product.SAFE/$file:10m:$srs" "$tifpath/$product"_10m.tif
    $gdalwarp -of GTiff -crop_to_cutline -cutline $cutline "$gdalS2prefix:$path/$product.SAFE/$file:20m:$srs" "$tifpath/$product"_20m.tif
    $gdalwarp -of GTiff -crop_to_cutline -cutline $cutline "$gdalS2prefix:$path/$product.SAFE/$file:60m:$srs" "$tifpath/$product"_60m.tif

done <$path/results.txt
