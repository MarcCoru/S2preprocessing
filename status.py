import sys, os
from configobj import ConfigObj
import re
import shutil

"""
Quick status script to get overview over products in different processing stages
"""

cfg_path=sys.argv[1]

cfg = ConfigObj(cfg_path)

project=cfg["project"].replace('$HOME',os.environ["HOME"])
path=cfg["path"].replace('$project',project)

print "Status report:"
print "site: {}".format(cfg_path)

if not os.path.exists(os.path.join(path,"results.txt")):
    print "No query results.txt available"
    print "run '$shj query.sh {}' to query for available products".format(cfg_path)


with open(os.path.join(path,"results.txt")) as f:
    queriedproducts = f.readlines()


dircontent=os.listdir(path)

L1C=[]
L2A=[]
L1Ctif=[]
L2Atif=[]
for el in dircontent:
    if el.endswith('SAFE'):
        if 'L1C' in el:
            L1C.append(el)
        elif 'L2A' in el:
            L2A.append(el)
    if el.endswith('tif'):
        if 'L1C' in el:
            L1Ctif.append(el)
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
print "\t{} L2A Products not completed! ({})".format(len(L2A_not_complete),L2A_not_complete)
print "{} tif converted Products with processing level L1C".format(len(L1Ctif))
print "{} tif converted Products with processing level L2A".format(len(L2Atif))
