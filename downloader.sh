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

java -jar ProductDownload/ProductDownload.jar \
 --mode RESUME \
 --sensor S2 \
 -a "$area" \
 --aws \
 --startdate $startdate \
 --enddate $enddate \
 --out $L1Czip \
 --store AWS \
 --cloudpercentage $maxcloud \
 --user $ESA_USERNAME \
 --password $ESA_PASSWORD \
 --verbose

#
# --aws \
#  --input $L1Cfolder \
