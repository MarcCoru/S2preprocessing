#!/bin/bash


# read configs
. $1

cat $path/results.txt | while read product
do
    
    if [ ! -d $path/$product.SAFE ]; then
        echo "downloading product: "$product
        sentinelhub.aws --product $product -f $path -e -t
    else
        echo "skipping product: "$product
    fi
done
