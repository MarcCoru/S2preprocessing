#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ];
  then
    echo Adds a boolean column to a postgresql table with a given split ratio
    echo
    echo "Usage: sh $0 site table columnname splitratio sqlwhere"
    echo ""
    echo "e.g. sh $0 sites/bavaria.site tiles train0 0.8 where eval=0 "
    echo "adds column 'train0' to 'tiles' table. Fills it with true/false"
    echo "in a t/f ratio of 0.8 where the eval field is false"
    exit 1
fi


# site config files (db connection attributes used)
site=$1
# table of tile geometry file
table=$2
columnname=$3 # eg eval, valid0, valid1
split=$4 # ratio between true and false
sqlwhere=$5 # e.g.  'where eval=0'

if [ -z "$site" ]
  then
    echo "No config file provided! Aborting"
    exit 1
fi

# read configs
. $site

# database connection
psql="psql -d $dbase --username=russwurm --host=$dbhost"

# add column
$psql -c "alter table $2 add column if not exists $columnname boolean;"

# insert '0' or '1' in split ratio
$psql -c "update $table set $columnname=(random() > $split) $sqlwhere;"
