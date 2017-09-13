from shapely.geometry import Point, box
import psycopg2
import numpy as np
import sys
from configobj import ConfigObj
import os
from geojson2aoi import geojson2aoi
import argparse


parser = argparse.ArgumentParser(description='created a grid in a database based on extent of geojson file. Requires fields: srs')
parser.add_argument('site', help='config file for specified site')
parser.add_argument('geojson', help="geojson file, which provides extent of AOI")
parser.add_argument('tablename', help="database tablename")
parser.add_argument('--tilesize', default=3000, help="Size of tiles in meter. Defaults to 3000m")
parser.add_argument('--margin', default=0, help="size of margin between tiles in meter")
args = parser.parse_args()

cfg_path=args.site

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
curs=conn.cursor()

srs=cfg["srs"].replace("_",":").lower()

aoi=geojson2aoi(args.geojson,srs=srs)
coords = np.array([coord.split(',') for coord in aoi.split(" ")]).astype(float).astype(int)

# AOI
x_min = coords[:,0].min()
y_min = coords[:,1].min()
x_max = coords[:,0].max()
y_max = coords[:,1].max() #
srs = int(srs.split(':')[-1]) # e.g. 'epsg:32632' -> 32632

rand = np.random.rand()

table_name = args.tablename

point_distance = args.tilesize - args.margin#m
offset = point_distance/2

commit_every = 1000

create_table_sql="""
    CREATE TABLE IF NOT EXISTS %s(
        id SERIAL NOT NULL PRIMARY KEY,
        geom geometry)
    """ % table_name
# Send it to PostGIS
print create_table_sql
curs.execute(create_table_sql)

x_grid = range(x_min+offset, x_max, point_distance)
y_grid = range(y_min+offset, y_max, point_distance)
n_points = len(x_grid)*len(y_grid)

count = 0
for x in x_grid:
    for y in y_grid:
        count += 1
        center = Point(x, y)

        geom = box(x-offset, y-offset, x+offset, y+offset)

        insert_sql = """
            INSERT INTO {0}(geom)
            VALUES (ST_SetSRID(%(geom)s::geometry, %(srid)s))
        """.format(table_name)

        curs.execute(
            insert_sql,
            {'geom': geom.wkb_hex, 'srid': srs})

        if count % commit_every == 0:
            conn.commit()
            print "count: %d/%d (%d%%), committing to db..." % (count, n_points, float(count)/float(n_points)*100)

print "creating spatial index..."
conn.commit()

curs.execute("CREATE INDEX point_idx ON %s USING GIST (geom);" % table_name)
conn.commit()

conn.close()
curs.close()
print "done..."
