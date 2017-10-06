#!/bin/bash

# Runs sen2cor on all products, which are located in the L1C folder (defined by site.cfg)
#
# usage sh sen2cor.sh site.cfg
#

# read configs
. $1

L2AProcess="Sen2Cor-2.4.0-Linux64/bin/L2A_Process"

fastskipmode=1

# default to project root config file if not set
if [ -z "$L2A_GIPP_path" ]; then
    L2A_GIPP_path=$project/cfg/L2A_GIPP.xml
fi

# for every line in the results file
cat $path/$queryfile | while read product
do

    L2Aproductname=$(echo $product | sed 's/MSIL1C/MSIL2A/g' | sed 's/OPER/USER/g' )

    echo $L2Aproductname

    if [ ! -d $path/$product.SAFE ]; then # target folder exists
        echo "source product $product does not exist -> skipping"
    elif [[ -d $path/$L2Aproductname.SAFE ]] && [[ $fastskipmode -eq 1 ]]; then # target folder exists
        echo "target product: $L2Aproductname already exists -> skipping"
    else # do sen2cor process in different threads
        echo "sen2cor: "$product" -> "$L2Aproductname
        $L2AProcess $path/$product.SAFE --GIP_L2A $L2A_GIPP_path > $path/$L2Aproductname.sen2cor
    fi
done

# delete folders of unsuccessfull processes (but leave log files)
#sh sen2cordeletefails.sh $1
