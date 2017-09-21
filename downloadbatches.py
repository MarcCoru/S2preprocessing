import psycopg2
import os
import gdal
import json
import numpy as np
from configobj import ConfigObj
import argparse
import datetime

import cPickle as pickle

import matplotlib.pyplot as plt

import pylab
from pylab import imshow, show, get_cmap
import pandas as pd

RASTER_NODATA_VALUE=0

with open('cfg/bands.json') as data_file:
    bandcfg = json.load(data_file)


def main():

    parser = argparse.ArgumentParser(
        description='created pickle files based on tiles in raster database')
    parser.add_argument('site', help='config file for specified site')
    parser.add_argument('level', help="either L1C or L2A")
    parser.add_argument('--subset', help="split 'n/m' tile ids in m subsets and only process the n subset")
    args = parser.parse_args()

    cfg_path = args.site

    cfg = ConfigObj(cfg_path)

    print
    conn = psycopg2.connect('postgres://{}:{}@{}/{}'.format(os.environ["POSTGIS_USER"],os.environ["POSTGIS_PASSWORD"],cfg['dbhost'],cfg['dbase']))

    level = args.level
    rastertable = cfg['dbtable']
    tiletable = cfg['tiletable']

    project = cfg["project"].replace('$HOME', os.environ["HOME"])
    tilefolder = cfg["tilefolder"].replace('$project', project)

    outfolder=os.path.join(tilefolder,tiletable)
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    ids = pd.read_sql("select id from {}".format(tiletable),conn)['id']

    # split tileids in subsets
    if args.subset:
        n,m = [int(i) for i in args.subset.split('/')]

        c = pd.cut(ids, m,labels=range(m))

        ids=ids.loc[c.loc[c==n].index]

        print "using subset {} of {}: length {}".format(n, m, len(ids))

    tileids = ids.values
    for tileid in tileids:
        print "{} downloading Tile {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tileid)
        download_tile(conn, level, rastertable, tiletable, outfolder, tileid,False)


def download_tile(conn, level, rastertable, tiletable, outfolder, tileid, verbose=False):
    def filename(tileid):
        return "{0:04d}.pkl".format(tileid)

    dates = pd.read_sql("select distinct date from {} where date is not null".format(rastertable),conn)["date"]
    querieddates=dates.sort_values().values

    def toidx(bands):
        return [bandcfg[level][rtype].index(b) + 1 for b in bands]

    # inspect tile if already exists
    outfile=os.path.join(outfolder,filename(tileid))
    if os.path.exists(outfile):
        with open(outfile,'rb') as f:
            tile = pickle.load(f)
    else:
        tile=None

    # create new empty sample
    ts = TimeSeriesSample(tile)
    for date in querieddates:

        if tile is not None:
            if date in tile['added']:
                if verbose: print "skipping {}, alreay in pickle file".format(date)
                continue

        if verbose: print date

        try:
            labels=queryLabel(conn, tiletable, tileid)

            raster=[]
            for rtype in ["10m","20m","60m"]:
                allbands = bandcfg[level][rtype]
                raster.append(queryRaster(conn, rastertable, tiletable, tileid, date, rtype, level, toidx(allbands)))

        except psycopg2.InternalError as err:
            print "Caught error {}".format(err)
            # add to the failed raster to avoid querying this file again...
            ts.addfailed(date)
            continue


        # add single time sample to timeseries
        ts.add(date, labels, raster[0],raster[1], raster[2])

    if verbose: print "writing to {}".format(outfile)
    ts.write_to_file(outfile)

    plt.show()

def queryRaster(conn, rastertable, tiletable, tileid, date, rtype, level, bands, verbose=False):
    curs = conn.cursor()
    # convert band names to band numbers using config file

    sql = """
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

    if verbose: print sql
    # following https://gis.stackexchange.com/questions/130139/downloading-raster-data-into-python-from-postgis-using-psycopg2

    # Use a virtual memory file, which is named like this
    vsipath = '/vsimem/from_postgis'

    # Download raster data into Python as GeoTIFF, and make a virtual file for GDAL
    curs.execute(sql)

    gdal.FileFromMemBuffer(vsipath, bytes(curs.fetchone()[0]))

    # Read first band of raster with GDAL
    ds = gdal.Open(vsipath)
    arrays = []
    for b in range(len(bands)):
        band = ds.GetRasterBand(b + 1)
        arrays.append(band.ReadAsArray())

    # Close and clean up virtual memory file
    ds = band = None
    gdal.Unlink(vsipath)
    curs.close()

    return np.stack(arrays, axis=2)


def buff2rast(buff):
    # Use a virtual memory file, which is named like this
    vsipath = '/vsimem/from_postgis'

    gdal.FileFromMemBuffer(vsipath, bytes(buff))

    # Read first band of raster with GDAL
    ds = gdal.Open(vsipath)
    band = ds.GetRasterBand(1)

    gdal.Unlink(vsipath)
    return np.flipud(band.ReadAsArray())


def queryLabel(conn, tiletable, tileid, verbose=False):
    curs = conn.cursor()
    # convert band names to band numbers using config file


    sql = """
    select st_astiff(
    st_clip(
    st_union(
        st_asraster(st_intersection(t.geom,l.geom), 
            10::float,10::float,st_xmin(t.geom)::float, st_xmax(t.geom)::float,'8BUI',l.labelid,-9999)
    ),
    t.geom, -9999)
    )
    from {tiletable} t, fields l 
    where t.id={tileid} and ST_Intersects(t.geom, l.geom)
    group by t.geom

    """.format(tileid=tileid, tiletable=tiletable)

    if verbose: print sql
    # following https://gis.stackexchange.com/questions/130139/downloading-raster-data-into-python-from-postgis-using-psycopg2

    # Download raster data into Python as GeoTIFF, and make a virtual file for GDAL
    curs.execute(sql)
    rs = curs.fetchone()[0]

    arr = buff2rast(rs)

    # Close and clean up virtual memory file

    curs.close()

    return arr


def drawlabels(conn, tiletable, tileid):
    labelmap = pd.read_sql('select distinct labelid, label from labelmap where labelid is not null order by labelid',
                           conn)

    def id2name(labelmap, labelid):
        return labelmap.loc[labelmap["labelid"] == labelid]["label"].values[0]

    fig, ax = plt.subplots()
    arr = queryLabel(conn, tiletable, tileid)
    im = ax.imshow(np.flipud(arr), cmap=get_cmap("Spectral"), interpolation='none')
    ax.set_title("Labels")
    uniques = np.unique(arr)

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_ticks(uniques)
    cbar.set_ticklabels([id2name(labelmap, t) for t in uniques])


def plot(tileid, date, level, conn, rastertable, tiletable):
    print date

    def m(rtype):

        def toidx(bands):
            return [bandcfg[level][rtype].index(b) + 1 for b in bands]

        allbands = bandcfg[level][rtype]
        return queryRaster(conn, rastertable, tiletable, tileid, date, rtype, level, toidx(allbands)), allbands

    arr, bands = m("10m")

    fig, axs = plt.subplots(1, 4, figsize=(14, 10))
    i = 0
    for ax in axs.reshape(-1):
        ax.imshow(arr[:, :, i], interpolation='none')
        ax.set_title(bands[i])
        i += 1

    arr, bands = m("20m")
    fig, axs = plt.subplots(2, 3, figsize=(10, 6))
    i = 0
    for ax in axs.reshape(-1):
        ax.imshow(arr[:, :, i], interpolation='none')
        ax.set_title(bands[i])
        i += 1

    arr, bands = m("60m")
    fig, axs = plt.subplots(1, 3, figsize=(9, 6))
    i = 0
    for ax in axs.reshape(-1):
        ax.imshow(arr[:, :, i], cmap=pylab.gray(), interpolation='none')
        ax.set_title(bands[i])
        i += 1

def queryDates(conn,table):
    curs=conn.cursor()
    return pd.read_sql("select distinct date from {}".format(table),conn)

class TimeSeriesSample():
    def __init__(self,tile):
        # 10 GSD, 20 GSD, 60 GSD, meta doy, year

        if tile is None:
            self.x10 = np.array([])
            self.x20 = np.array([])
            self.x60 = np.array([])
            self.y = np.array([])
            self.meta=np.array([])
            self.added = np.array([])
        else:
            self.x10 = tile['x10']
            self.x20 = tile['x20']
            self.x60 = tile['x60']
            self.y = tile['y']
            self.meta = tile['meta']

            # dates which did not pass validateInput
            self.added = tile['added']

    def validateInput(self, date, y, x10, x20, x60):
        """ Reject samples if needed (e.g. all raste values: <NoData>)"""

        if np.all(x10==RASTER_NODATA_VALUE) | np.all(x20==RASTER_NODATA_VALUE) | np.all(x60==RASTER_NODATA_VALUE):
            return False

        return True

    def as_dict(self):
        return {'meta':self.meta, 'x10':self.x10, 'x20':self.x20, 'x60':self.x60, 'y':self.y, 'added':self.added}

    # add a single time
    def add(self,date, y, x10,x20,x60):
        self.added = np.append(self.added, date)

        if not self.validateInput(date, y, x10, x20, x60):
            return None

        x10normalized = x10 * 1e-3
        x20normalized = x20 * 1e-3
        x60normalized = x60 * 1e-3

        # extract day of year and year from date
        #meta = np.array([date.timetuple().tm_yday / 365.,date.year - 2016])

        self.x10=np.append(self.x10,x10normalized)
        self.x20=np.append(self.x20, x20normalized)
        self.x60=np.append(self.x60, x60normalized)
        self.meta=np.append(self.meta, date)
        self.y=np.append(self.y, y)

    def addfailed(self,date):
        self.added = np.append(self.added, date)

    def write_to_file(self,filename):

        x10 = self.x10
        x20 = self.x20
        x60 = self.x60

        meta = self.meta

        y = self.y

        with open(filename, "wb") as f:
            pickle.dump(self.as_dict(), f, protocol=2)

    """
    def write_to_file(self,filename):

        def _int64_feature(value):
            return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

        def _bytes_feature(value):
            return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

        writer = tf.python_io.TFRecordWriter(filename)

        x10 = np.stack(self.x10)
        x20 = np.stack(self.x20)
        x60 = np.stack(self.x60)

        feature={}
        for data,text in zip([x10,x20,x60],['10m','20m','60m']):
            t,w,h,d = data.shape

            feature['{}dates'.format(text)] = _int64_feature(t)
            feature['{}width'.format(text)] = _int64_feature(w)
            feature['{}height'.format(text)] = _int64_feature(h)
            feature['{}depth'.format(text)] = _int64_feature(d)
            feature['{}image'.format(text)] = _bytes_feature(data.tostring())



        features=tf.train.Features(feature=feature)

        example = tf.train.Example(features=features)

        writer.write(example.SerializeToString())
        return 0
    """



if __name__ == "__main__":
    main()