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

gdalwarp="conda/bin/gdalwarp"

# for every line in the results file
cat $path/results.txt | while read p
do
    
    # select product name
    if [ "$level" = "L1C" ]; then
        product=$p
    elif [ "$level" = "L2A" ]; then
        product=$(echo $p | sed 's/MSIL1C/MSIL2A/g' | sed 's/OPER/USER/g' )
    fi
    
    echo $product
    
    file=$(ls $path/$product.SAFE/MTD*.xml)
    $gdalwarp -of GTiff -crop_to_cutline -cutline $cutline "$gdalS2prefix:$file:10m:$srs" "$path/$product"_10m.tif
done
