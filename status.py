import sys, os
from configobj import ConfigObj
import re
import shutil
import argparse

"""
Quick status script to get overview over products in different processing stages
"""


parser = argparse.ArgumentParser(description='Query some status information')
parser.add_argument('site', type=str, help='configuration file')
parser.add_argument('-v','--verbose', action='store_true',help="list individual files")

args = parser.parse_args()

cfg_path=args.site

cfg = ConfigObj(cfg_path)

project=cfg["project"].replace('$HOME',os.environ["HOME"])
path=cfg["path"].replace('$project',project)

queryfile=cfg["queryfile"]

print "Status report:"
print "site: {}".format(cfg_path)

if not os.path.exists(os.path.join(path,queryfile)):
    print "No query $queryfile available"
    print "run '$shj query.sh {}' to query for available products".format(cfg_path)


with open(os.path.join(path,queryfile)) as f:
    queriedproducts = f.readlines()
# trim newlines
queriedproducts=[el.replace('\n','') for el in queriedproducts]
dircontent=os.listdir(path)

L1C=[]
L2A=[]
L1C10tif=[]
L1C20tif=[]
L1C60tif=[]
L2Atif=[]
for el in dircontent:
    if el.endswith('SAFE'):
        if 'L1C' in el:
            L1C.append(el)
        elif 'L2A' in el:
            L2A.append(el)
    if el.endswith('tif'):
        if 'L1C' in el:
            if el.endswith("_10m.tif"):
                L1C10tif.append(el)
            elif el.endswith("_20m.tif"):
                L1C20tif.append(el)
            elif el.endswith("_60m.tif"):
                L1C60tif.append(el)

        elif 'L2A' in el:
            L2Atif.append(el)

L2A_not_complete=[]
for el in L2A:
    logfile=el.replace(".SAFE",".sen2cor")
    with open(os.path.join(path,logfile)) as f:
        lastline = f.readlines()[-1]
        if not 'Progress[%]: 100.00' in lastline:
            L2A_not_complete.append(el)

print "{} L1C products queried".format(len(queriedproducts))
print "{} Products with processing level L1C".format(len(L1C))
print "{} Products with processing level L2A".format(len(L2A))
print "\t{} L2A Products not completed:".format(len(L2A_not_complete))
if args.verbose: print "\t{}".format("\n\t".join(L2A_not_complete))
print "{} 10m, {} 20m, {} 60m tif converted Products with processing level L1C".format(len(L1C10tif),len(L1C20tif),len(L1C60tif))
print "{} tif converted Products with processing level L2A".format(len(L2Atif))

# downloaded products, which are not in $queryfile
danglingProducts=[]
for el in dircontent:
    if (el.endswith('.SAFE')) and ('L1C' in el):
        productname=el.split('.')[0]
        if productname not in queriedproducts:
            danglingProducts.append(el)

print "{} L1C products are present, but not part of {}".format(len(danglingProducts),queryfile)
if args.verbose: print "\t{}".format("\n\t".join(danglingProducts))
