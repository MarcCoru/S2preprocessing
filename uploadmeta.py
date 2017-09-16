import psycopg2
import os
import sys
from configobj import ConfigObj
import pandas as pd
import re
import datetime

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
cur = conn.cursor()

# needs to be executed while no other process accesses table...
if True:
    # create attributes if not exists
    sql="""
    ALTER TABLE {0} ADD COLUMN IF NOT EXISTS year integer;
    ALTER TABLE {0} ADD COLUMN IF NOT EXISTS doy integer;
    ALTER TABLE {0} ADD COLUMN IF NOT EXISTS date date;
    ALTER TABLE {0} ADD COLUMN IF NOT EXISTS level varchar(5);
    ALTER TABLE {0} ADD COLUMN IF NOT EXISTS sat varchar(5);
    ALTER TABLE {0} ADD COLUMN IF NOT EXISTS type varchar(5);
    """.format(cfg['dbtable'])
    cur.execute(sql)
    conn.commit()

# select filenames, which lack meta values
sql="""
select distinct filename from {}
where
year is NULL or
doy is NULL or
date is NULL or
level is NULL or
sat is NULL or
type is NULL
""".format(cfg['dbtable'])

# old format: e.g.
#S2A_USER_PRD_MSIL2A_PDMC_20160831T224638_R065_V20160830T102022_20160830T102052
#S2oldformat=".{3}_.{4}_.{3}_.{6}_.{4}_.{15}_.{4}_.{16}_.{16}.*"

# new format: e.g.
# S2A_MSIL1C_20170616T102021_N0205_R065_T32UQV_20170616T102331_60m.tif
#S2newformat=".{3}_.{6}_.{15}_.{5}_.{4}_.{6}_.{15}.*"

rs = pd.read_sql(sql, conn)

for filename in rs["filename"]:
    print filename
    sat=re.search(r"S2A|S2B",filename).group(0)
    level=re.search(r"L1C|L2A",filename).group(0)
    datestr=re.search(r"_[0-9]{8}T",filename).group(0)[1:-1] # remove "_" and "T"
    date=datetime.datetime.strptime(datestr,"%Y%m%d")
    doy=date.timetuple().tm_yday
    year=date.year
    stype=re.search(r"(.{3})\.tif",filename).group(1)

    print "parsed: sat {}, level {}, date {}, doy {}, year {}, type {} from {}".format(sat,level,date.date(),doy,year,stype,filename)

    updatesql="""
    update {}
    set
        sat=%s,
        level=%s,
        date=%s,
        doy=%s,
        year=%s,
        type=%s
    where
        filename='{}';
    """.format(cfg['dbtable'],filename)

    cur.execute(updatesql, (sat,level,date,doy,year,stype))

conn.commit()
cur.close()
conn.close()
