import psycopg2
from configobj import ConfigObj
import sys
import os
import gdal
import json
import datetime
import numpy as np
import pandas as pd

def main():
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

    with open('cfg/bands.json') as data_file:
        bandcfg = json.load(data_file)

    conn = psycopg2.connect('postgres://{}:{}@{}/{}'.format(os.environ["POSTGIS_USER"],os.environ["POSTGIS_PASSWORD"],cfg['dbhost'],cfg['dbase']))

    rastertable="bavaria"
    tiletable="tiles480"

    tileid=1
    date=datetime.datetime(2016,4,13)
    rtype="10m"
    level="L1C"
    bands=["B2","B3","B4","B8"]

    bandidxs=[bandcfg[level][rtype].index(b)+1 for b in bands]

    img = queryRaster(conn,rastertable,tiletable, tileid, date, rtype, level, bandidxs)
    # print img.shape

    ### query raster(tileid, date, type, level)
def queryDates(conn,table):
    curs=conn.cursor()
    return pd.read_sql("select distinct date from {}".format(table),conn)


def queryRaster(conn,rastertable,tiletable, tileid, date, rtype, level, bands):
    curs=conn.cursor()
    # convert band names to band numbers using config file


    sql="""
        select
        	ST_astiff(ST_UNION(ST_CLIP(r.rast, t.geom)),ARRAY{bands})
        from
        	{rastertable} r, {tiletable} t
        where
        	t.id={tileid} and
            ST_INTERSECTS(r.rast,t.geom) and
            r.type='{rtype}' and
            r.level='{level}' and
            date='{date}'
        """.format(rastertable=rastertable,
        tiletable=tiletable,
        tileid=tileid,
        rtype=rtype,
        level=level,
        date=date.strftime("%Y-%m-%d"),
        bands=bands)

    print sql
    # following https://gis.stackexchange.com/questions/130139/downloading-raster-data-into-python-from-postgis-using-psycopg2

    # Use a virtual memory file, which is named like this
    vsipath = '/vsimem/from_postgis'

    # Download raster data into Python as GeoTIFF, and make a virtual file for GDAL
    curs.execute(sql)
    gdal.FileFromMemBuffer(vsipath, bytes(curs.fetchone()[0]))

    # Read first band of raster with GDAL
    ds = gdal.Open(vsipath)
    arrays=[]
    for b in range(len(bands)):
        band = ds.GetRasterBand(b+1)
        arrays.append(band.ReadAsArray())

    # Close and clean up virtual memory file
    ds = band = None
    gdal.Unlink(vsipath)
    curs.close()

    return np.stack(arrays,axis=2)

if __name__ == "__main__":
    # execute only if run as a script
    main()
