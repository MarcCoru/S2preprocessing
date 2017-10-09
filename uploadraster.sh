#!/bin/bash

if [ ! "$1"="--help" ] || [ -z "$1" ] || [ -z "$2" ];
  then
    echo "uploads all raster specified in the site file to the database table"
    echo ""
    echo "bash uploadraster.sh sites/bavaria.site L1C"
    exit 1
fi

# read configs
. $1

# either L1C or L2A
level=$2


psql -d $dbase -c "Create table if not exists $dbtable(rid serial primary key, rast raster, filename text);"

# database connection
psql="psql -d $dbase --username=russwurm --host=$dbhost"

# check if table already exists
if [ $($psql -tAc "SELECT 1 FROM pg_tables where tablename='$dbtable'") = '1' ]; then
    echo "appending to DB"
    appendflag="-a"
else
    appendflag="-I" # first insert should also create an index
fi

# database exists
    # $? is 0

#files="data/bavaria/test/S2A_OPER_PRD_MSIL1C_PDMC_20160522T182438_R065_V20160522T102029_20160522T102029_10m.tif"

# query already present products
productsindb=$($psql -c "Select distinct filename from $dbtable")


echo $psql
while read p;
do

    # select product name
    if [ "$level" = "L1C" ]; then
        product=$p
    elif [ "$level" = "L2A" ]; then
        # predict L2A product name
        product=$(echo $p | sed 's/MSIL1C/MSIL2A/g' | sed 's/OPER/USER/g' )
    fi

    # query if filename does not already exists
    #echo $filename
    if [[ "$productsindb" = *"$product"* ]] ; then
      echo "product $p already in database table $dbtable. skipping..."
      continue
    fi
    echo "loading $p to database"
    raster2pgsql -s $srs $appendflag -P $tifpath/$product*.tif -F -t $tilesize"x"$tilesize $dbtable | $psql
    #raster2pgsql -s $srs $appendflag -P -C -M $tifpath/$product*.tif -F -t $tilesize"x"$tilesize $dbtable > uploadsql/$product.sql
done <$path/$queryfile
# type := 10m, 20m, 60m or SCL

# add columns
$psql <<EOF
\x
ALTER TABLE $dbtable ADD COLUMN IF NOT EXISTS year integer;
ALTER TABLE $dbtable ADD COLUMN IF NOT EXISTS doy integer;
ALTER TABLE $dbtable ADD COLUMN IF NOT EXISTS date date;
ALTER TABLE $dbtable ADD COLUMN IF NOT EXISTS level varchar(5);
ALTER TABLE $dbtable ADD COLUMN IF NOT EXISTS sat varchar(5);
ALTER TABLE $dbtable ADD COLUMN IF NOT EXISTS type varchar(5);
EOF

# add meta information
#$project/conda/bin/python uploadmeta.py $1
