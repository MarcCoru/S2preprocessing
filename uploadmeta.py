import psycopg2
import os
import sys
from configobj import ConfigObj
import pandas as pd
import re

if len(sys.argv) < 2:
    print "No config file provided! Aborting"
    sys.exit()

cfg_path=sys.argv[1]

cfg = ConfigObj(cfg_path)

def setdefault(key,value):
    if key not in cfg.keys():
        print "WARNING: {} not specified in {}, defaulting to '{}'".format(key,cfg_path, value)
        cfg[key]=value
# set defaults if not defined

setdefault('dbhost','dbserver')
setdefault('dbase','fields')
setdefault('dbtable','test')

conn = psycopg2.connect('postgres://{}:{}@{}/{}'.format(os.environ["POSTGIS_USER"],os.environ["POSTGIS_PASSWORD"],cfg['dbhost'],cfg['dbase']))

# select filenames, which lack meta values
sql="""
select distinct filename from {}
where
year is NULL or
doy is NULL or
date is NULL or
level is NULL or
sat is NULL or
tile is NULL or
type is NULL
""".format(cfg['dbtable'])

# old format: e.g.
#S2A_USER_PRD_MSIL2A_PDMC_20160831T224638_R065_V20160830T102022_20160830T102052
S2oldformat=".{3}_.{4}_.{3}_.{6}_.{4}_.{15}_.{4}_.{16}_.{16}.*"

# new format: e.g.
# S2A_MSIL1C_20170616T102021_N0205_R065_T32UQV_20170616T102331_60m.tif
S2newformat=".{3}_.{6}_.{15}_.{5}_.{4}_.{6}_.{15}.*"

rs = pd.read_sql(sql, conn)
#cur = conn.cursor()conda
for f in rs["filename"]:

    print f
