import sys, os
from configobj import ConfigObj
import re
import shutil
import argparse

"""
Quick status script to get overview over products in different processing stages
"""

def main(args):
    cfg_path=args.site

    cfg = ConfigObj(cfg_path)

    project=cfg["project"].replace('$HOME',os.environ["HOME"])
    path=cfg["path"].replace('$project',project)
    tifpath=cfg["tifpath"].replace('$project',project)

    queryfile=cfg["queryfile"]

    print "Status report:"
    print "site: {}".format(cfg_path)

    if not os.path.exists(os.path.join(path,queryfile)):
        print "No query $queryfile available"
        print "run '$sh query.sh {}' to query for available products".format(cfg_path)
        sys.exit()

    with open(os.path.join(path,queryfile)) as f:
        queriedproducts = f.readlines()

    # trim newlines
    queriedproducts=[el.replace('\n','') for el in queriedproducts]
    dircontent=os.listdir(path)
    tifdircontent=os.listdir(path)

    def l1ctol2a(product):
        return product.replace('L1C','L2A').replace('OPER','USER')

    L1C=[]
    L2A=[]
    L1C10tif=[]
    L1C20tif=[]
    L1C60tif=[]
    L2Atif=[]
    for product in queriedproducts:
        if product+".SAFE" in dircontent:
            L1C.append(product)
        if l1ctol2a(product)+".SAFE" in dircontent:
            L2A.append(l1ctol2a(product))
        if product+"_10m.tif" in dircontent:
            L1C10tif.append(product)
        if product+"_20m.tif" in dircontent:
            L1C20tif.append(product)
        if product+"_60m.tif" in dircontent:
            L1C10tif.append(product)
        if l1ctol2a(product)+"_10m.tif" in dircontent:
            L2Atif.append(l1ctol2a(product))

    L2A_not_complete=[]
    for el in L2A:
        logfile=el + ".sen2cor"
        with open(os.path.join(path,logfile)) as f:
            lastline = f.readlines()[-1]
            if not 'Progress[%]: 100.00' in lastline:
                L2A_not_complete.append(el)
                if args.cleanfailedsen2cor:
                    print "deleting failed sen2cor (lastline: '{}') {}".format(lastline,os.path.join(path,el+".SAFE"))
                    shutil.rmtree(os.path.join(path,el+".SAFE"))

    print "{} L1C products queried".format(len(queriedproducts))
    print "{} Products with processing level L1C".format(len(L1C))
    print "{} Products with processing level L2A".format(len(L2A))
    print "\t{} L2A Products not completed. Delete via --cleanfailedsen2cor".format(len(L2A_not_complete))
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

    def cleanempty(productlist):
        # check number of granules in products
        productswithoutgranules=[]
        for el in productlist:
            p = os.path.join(path,el+".SAFE","GRANULE")

            # skip non present
            if not os.path.exists(p):
                productswithoutgranules.append(el)
                continue


            if len(os.listdir(p))==0:
                if args.delemptyproducts:
                    print "deleting {}".format(os.path.join(path,el+".SAFE"))
                    shutil.rmtree(os.path.join(path,el+".SAFE"))
                else:
                    # count for inventory
                    productswithoutgranules.append(el)
        return productswithoutgranules


    empty = cleanempty(L1C)
    if not args.delemptyproducts: print "{} empty L1C products (no granules). To delete enable the --delemptyproducts flag".format(len(empty))
    if args.verbose: print "\t{}".format("\n\t".join(empty))

    empty = cleanempty(L2A)
    if not args.delemptyproducts: print "{} empty L2A products (no granules). To delete enable the --delemptyproducts flag".format(len(empty))
    if args.verbose: print "\t{}".format("\n\t".join(empty))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Query some status information')
    parser.add_argument('site', type=str, help='configuration file')
    parser.add_argument('--delemptyproducts', action='store_true', help="deletes empty products")
    parser.add_argument('--cleanfailedsen2cor', action='store_true', help="deletes failed sen2cor products")
    parser.add_argument('-v','--verbose', action='store_true',help="list individual files")
    args = parser.parse_args()

    main(args)
