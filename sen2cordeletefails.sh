#!bin/bash

# read configs
. $1

path=$L1C

sucess="Progress[%]: 100.00 : Application terminated successfully."

# delete all folders, which have not 'Progress[%]: 100.00 : Application terminated successfully.' at last log line
# for every line in the results file
cat $path/results.txt | while read product
do
   # skip if already exists
   L2Aproductname=$(echo $product | sed 's/MSIL1C/MSIL2A/g' | sed 's/OPER/USER/g' )
   echo $L2Aproductname
   
   # skip if no logfile exists
   if [ ! -f "$path/$L2Aproductname.sen2cor" ]
      then
      continue
   fi
   
   lastlog=$(tail -n 1 $path/$L2Aproductname.sen2cor)
   #echo $lastlog
   # if last logging entry does not indicate success
   if [ "$lastlog" != "$sucess" ]; then
      
      # delete folder if still exists
      echo removing $L2Aproductname.SAFE
      rm -fr $path/$L2Aproductname.SAFE
   fi
done
