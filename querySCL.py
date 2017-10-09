import pandas as pd
import psycopg2
import argparse
import os
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Query database for rasters. Requires POSTGIS_USER and POSTGIS_PASSWORD environment variables to be set')
    parser.add_argument('filename', type=str, help='csv filename')
    parser.add_argument('--db', type=str, default="fields", help='database (default fields)')
    parser.add_argument('--host', type=str, default="dbserver", help='database (default dbserver)')

    args = parser.parse_args()

    filename=args.filename

    conn = psycopg2.connect('postgres://{}:{}@{}/{}'.format(os.environ["POSTGIS_USER"],os.environ["POSTGIS_PASSWORD"],args.host,args.db))

    dates = pd.read_sql('Select distinct date from bavaria order by date',conn)["date"].sort_values().values

    frames=[]
    for date in dates:
        print "{}: query product from {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), date.strftime("%Y-%m-%d"))
        frames.append(querySCLhist(date,conn))

    out = pd.concat(frames)
    out.to_csv(filename)

def querySCLhist(date, conn):
    """ Query database for raster at defined date. Look at SCL band (=12) and count values 
    returns one lined Dataframe index=date and columns sclnames"""

    sclnames=['nodata',
         'defect',
         'darkfeat',
         'cloud shadow',
         'vegetation', 
         'bare soil', 
         'water', 
         'cloud low prob', 
         'cloud med prob', 
         'cloud high prob', 
         'cloud cirrus', 
         'snow']

    scldict={}
    for i in range(len(sclnames)):
        scldict[i+1] = sclnames[i]

    # band12 -> SCL
    sql="""
    SELECT (stats).value as SCL,(stats).count 
    FROM (
        select ST_ValueCount(st_union(rast),12) as stats 
        from bavaria where date='{date}'::date and level='L2A' and type='20m'
        ) as foo
    """.format(date=date.strftime("%Y-%m-%d"))

    sclhist = pd.read_sql(sql,conn)
    sclhist["scl"]=sclhist.scl.map(scldict) # replace pixel value with name
    sclhist = sclhist.set_index("scl").T
    sclhist.index=pd.to_datetime([date])
    return sclhist



if __name__ == "__main__":
    main()



