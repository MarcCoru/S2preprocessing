import sys, os
from configobj import ConfigObj
import re
import shutil

cfg_path=sys.argv[1]

cfg = ConfigObj(cfg_path)

# set dryrun flat
dryrun=False
if len(sys.argv) > 2:
    dryrun=sys.argv[2]=='-d'

if dryrun:
    print "dryrun flag ('-d') active, no deletions"

if "granules" not in cfg.keys():
    print "no variable 'granules' in {} specified, nothing to delete...".format(cfg_path)
    sys.exit()

relevantgranules=cfg["granules"].replace(" ","|")
project=cfg["project"].replace('$HOME',os.environ["HOME"])
path=cfg["path"].replace('$project',project)

regex=".*("+relevantgranules+").*"
p = re.compile(regex)

# some statistics
nproducts=0
ngranules=0
ngrkept=0
ngrdeleted=0

for product in os.listdir(path):

    # skip files
    if os.path.isfile(os.path.join(path,product)):
        continue
    nproducts+=1

    granules = os.listdir(os.path.join(path,product,"GRANULE"))

    # for every granule in product
    for granule in granules:

        #skip if not folder
        if os.path.isfile(os.path.join(path,product,"GRANULE",granule)):
            continue
        
        ngranules+=1

        # if not matches required Granules
        if p.match(granule) is None:
            print "granule {} does not match regex {} -> deleting...".format(granule,regex)
            ngrdeleted+=1
            if not dryrun: shutil.rmtree(os.path.join(path,product,"GRANULE",granule))
        else:
            ngrkept+=1

print
print "SUMMARY: {} products inspected, {} granules checked, {} deleted, {} kept".format(nproducts,ngranules,ngrdeleted,ngrkept)

