#!/bin/bash

# Runs sen2cor on all products, which are located in the L1C folder (defined by site.cfg)
#
# usage sh sen2cor.sh site.cfg
#

# read configs
. $1

L2AProcess="Sen2Cor-2.4.0-Linux64/bin/L2A_Process"

# default to project root config file if not set
if [ -z "$L2A_GIPP_path" ]; then
    L2A_GIPP_path=$project/L2A_GIPP.xml
fi

# for every line in the results file
cat $path/results.txt | while read product
do
    
    L2Aproductname=$(echo $product | sed 's/MSIL1C/MSIL2A/g' | sed 's/OPER/USER/g' )
    
    echo $L2Aproductname
    
    if [ -d $path/$L2Aproductname.SAFE ]; then # target folder exists
        echo "skipping product: "$product
    else # do sen2cor process in different threads
        echo "sen2cor: "$product" -> "$L2Aproductname
        $L2AProcess $path/$product.SAFE --GIP_L2A $L2A_GIPP_path > $path/$L2Aproductname.sen2cor
    fi
done

# delete folders of unsuccessfull processes (but leave log files)
#sh sen2cordeletefails.sh $1
