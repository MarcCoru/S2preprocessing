#!/bin/bash

# insert config file as first argument
#
# $ sh downloader.sh bavaria.download

# download product downloader if not exists
if [ ! -f ProductDownload/ProductDownload.jar ]; then
    sh setup.sh
fi

# Assertions
if [ -z "$1" ]; then
    echo "No config file provided! Aborting"
    exit 1
fi
if [ ! -f $1 ]; then
    echo "Config file $1 not found! Aborting"
    exit 1
fi

# read configs
. $1

echo $startdate

# seems not to work for 2017 so query-> $queryfile
java -jar ProductDownload/ProductDownload.jar $2 \
--mode RESUME \
--sensor S2 \
--aws \
-a $area \
--startdate $startdate \
--enddate $enddate \
--out "$path" \
--cloudpercentage $maxcloud \
--verbose \
--store AWS \
--q

# rename $queryfile to queryfile name
mv $path/results.txt $path/$queryfile

#--unpacked
#
# --aws \
#  --input $L1Cfolder \


#cat $L1C/$queryfile | while read product
#do
#   echo $product # do something with $line here
#   #sentinelhub.aws --product $product -f $L1C -e -t
#done

#sentinelhub.aws --product S2A_OPER_PRD_MSIL1C_PDMC_20160908T083647_R022_V20160906T101022_20160906T101558 -f . -e
