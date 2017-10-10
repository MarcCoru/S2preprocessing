#!/bin/bash


# read configs
. $1

numdownload=$(cat $path/download.todo | wc -l)

echo "downloading "$numdownload" products"

cat $path/download.todo | while read product
do

    if [ ! -d $path/$product.SAFE ]; then
        echo "downloading product: "$product
        sentinelhub.aws --product $product -f $path -e -t
    else
        echo "skipping product: "$product
    fi
done
