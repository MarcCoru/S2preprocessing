#!/bin/bash


# read configs
. $1

cat $L1C/results.txt | while read product
do
   
   if [ ! -d $L1C/$product.SAFE ]; then
      echo "downloading product: "$product
      sentinelhub.aws --product $product -f $L1C -e -t
   else
      echo "skipping product: "$product
   fi
done
