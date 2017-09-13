#!/usr/bin/env python

import json
import pyproj
import re
import argparse

"""
projects polygon nodes of input geojson file to WGS84 (epsg:4326) and prints
list of longitude and latitude.
Only the first feature is considered.

converts projected geojson to list format of https://github.com/kraftek/awsdownload
"""

def geojson2aoi(geojson_file,srs="epsg:4326"):
    with open(geojson_file,"r") as f:
        js = json.load(f)

    target_proj = pyproj.Proj(init=srs) # wgs84 lon lat
    source_proj = pyproj.Proj(init=getsrs(js)) # extract from geojson

    # Point list of the first feature
    pts = js["features"][0]["geometry"]["coordinates"][0]

    lines = []
    for pt in pts:
        lon, lat = pyproj.transform(source_proj,target_proj,pt[0],pt[1])
        lines.append("{},{}".format(lon,lat))

    aoi = " ".join(lines)
    return aoi

def getsrs(geojson):
    # regex to find crs
    regex = "EPSG:{1,2}[0-9]{4,5}"

    m = re.search(regex, str(geojson))

    if m is None: # default to wgs84
        return "epsg:4236"
    epsg = m.group(0)
    epsg = epsg.replace("::",":").lower()
    return epsg

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='converts geojson containing one polygon to a list of wgs84 (epsg:4236) coordinates. If multiple features are in the geojson only the first is considered')
    parser.add_argument('geojson', help='path to the input geojson file')
    parser.add_argument('--srs', default='epsg:4326', help="target srs coordinate system. Defaults to 'epsg:4326'")
    args = parser.parse_args()

    ## debug
    #args.geojson="data/shp/bavaria/aoi.geojson"
    #args.geojson="data/shp/ecuador/Ecuador_AOI.geojson"
    #args.aoi="download/bavaria.aoi"

    print(geojson2aoi(args.geojson,srs=args.srs))
