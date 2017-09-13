#!/bin/sh

# read configs
. $1

if [ -z "$1" ]
  then
    echo "No config file provided! Aborting"
    exit 1
fi


# database connection
psql="psql -d $dbase --username=russwurm"

#files="data/bavaria/test/S2A_OPER_PRD_MSIL1C_PDMC_20160522T182438_R065_V20160522T102029_20160522T102029_10m.tif"

echo $psql
raster2pgsql -s $srs -I -C -M $tifpath/*.tif -F -t 100x100 $dbtable | $psql

# add columns
$psql <<EOF
\x
ALTER TABLE $dbtable ADD COLUMN IF NOT EXISTS year integer;
ALTER TABLE $dbtable ADD COLUMN IF NOT EXISTS doy integer;
ALTER TABLE $dbtable ADD COLUMN IF NOT EXISTS date date;
ALTER TABLE $dbtable ADD COLUMN IF NOT EXISTS level varchar(5);
ALTER TABLE $dbtable ADD COLUMN IF NOT EXISTS sat varchar(5);
ALTER TABLE $dbtable ADD COLUMN IF NOT EXISTS tile varchar(6);
ALTER TABLE $dbtable ADD COLUMN IF NOT EXISTS res varchar(5);
EOF
