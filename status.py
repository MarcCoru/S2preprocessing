from configobj import ConfigObj
import os
import glob
from os.path import join
import pandas as pd
import argparse
from progressbar import *               # just a simple progress bar


def main():
    parser = argparse.ArgumentParser(description='Creates status csv and todo lists')
    parser.add_argument('site', type=str, default='sites/bavaria.site',help='config file describing site paramters')
    parser.add_argument('-noupdate',action='store_true',help='print info, but dont overwrite todo and status files')
    args = parser.parse_args()
    configpath = args.site

    cfg = ConfigObj(configpath)

    cfg["project"] = cfg["project"].replace('$HOME', os.environ["HOME"])
    cfg["path"] = cfg["path"].replace('$project', cfg["project"])
    cfg["tifpath"] = cfg["tifpath"].replace('$project', cfg["project"])

    print "looking for products..."
    status_df = look_for_products(cfg)
    status_df = append_todos(status_df)

    print_status(cfg,status_df)

    print
    if not args.noupdate:
        print "updating status.csv and todo lists..."
        write_status_and_todos(cfg, status_df)
    else:
        print "no updates..."

def print_status(cfg,status_df):
    print "Found {} queried products".format(status_df.shape[0])
    print
    print "Processing Level L1C:"
    print "  {} SAFE products".format(status_df[status_df["L1C"]].shape[0])
    print "  {} SAFE products without Granules".format(status_df[status_df["nogranules"]].shape[0])
    print "    {} tif 10m products".format(status_df[status_df["L1Ctif10"]].shape[0])
    print "    {} tif 20m products".format(status_df[status_df["L1Ctif20"]].shape[0])
    print "    {} tif 60m products".format(status_df[status_df["L1Ctif60"]].shape[0])
    print "    {} products in cropL1C.todo".format(status_df[status_df["do_cropL1C"]].shape[0])
    print
    print "Processing Level L2A:"
    print "  {} SAFE products".format(status_df[status_df["L2A"]].shape[0])
    print "  {} products in sen2cor.todo".format(status_df[status_df["do_sen2cor"]].shape[0])
    print "    {} tif 10m products".format(status_df[status_df["L2Atif10"]].shape[0])
    print "    {} tif 20m products".format(status_df[status_df["L2Atif20"]].shape[0])
    print "    {} tif 60m products".format(status_df[status_df["L2Atif60"]].shape[0])
    print "    {} products in cropL2A.todo".format(status_df[status_df["do_cropL2A"]].shape[0])
    print
    print "detailed information at:"
    print join(cfg["path"],"status.csv")
    print
    print "query"
    print join(cfg["path"],cfg["queryfile"])
    print
    print "Todo lists:"
    print join(cfg["path"],"sen2cor.todo")
    print join(cfg["path"],"cropL1C.todo")
    print join(cfg["path"],"cropL2A.todo")

def look_for_products(cfg):

    SAFE = glob.glob(cfg["path"] + "/*.SAFE")
    tif = glob.glob(cfg["tifpath"] + "/*.tif")

    with open(join(cfg["path"], cfg["queryfile"]), 'r') as f:
        queries = f.read().splitlines()

    def l1ctol2a(product):
        return product.replace("OPER", "USER").replace("L1C", "L2A")

    # create empty dataframe
    df = pd.DataFrame(index=queries)

    widgets = ['looking for products: ', Percentage(), ' ', Bar(marker='#', left='[', right=']'),
               ' ', ETA()]  # see docs for other options

    pbar = ProgressBar(widgets=widgets, maxval=df.shape[0])
    pbar.start()

    # for each product in queryfile
    i = 0
    for product, row in df.iterrows():
        pbar.update(i)
        i+=1
        # check if L1C product exists in $path
        df.loc[product, "L1C"] = os.path.exists(
            join(cfg["path"], product + ".SAFE"))

        # check if product has no granules
        if os.path.exists(join(cfg["path"], product + ".SAFE", "GRANULE")):
            df.loc[product, "nogranules"] = len(os.listdir(join(cfg["path"], product + ".SAFE", "GRANULE")))==0
        else: # if no product in present give benefit of doubt
            df.loc[product, "nogranules"] = False

        # check if L2A product exists in $path
        df.loc[product, "L2A"] = os.path.exists(
            join(cfg["path"], l1ctol2a(product) + ".SAFE"))

        # L1C: check if 10,20,60m tifs exist in $tifpath
        df.loc[product, "L1Ctif10"] = os.path.exists(
            join(cfg["tifpath"], product + "_10m.tif"))
        df.loc[product, "L1Ctif20"] = os.path.exists(
            join(cfg["tifpath"], product + "_20m.tif"))
        df.loc[product, "L1Ctif60"] = os.path.exists(
            join(cfg["tifpath"], product + "_60m.tif"))

        # L2A: check if 10,20,60m tifs exist in $tifpath
        df.loc[product, "L2Atif10"] = os.path.exists(
            join(cfg["tifpath"], l1ctol2a(product) + "_10m.tif"))
        df.loc[product, "L2Atif20"] = os.path.exists(
            join(cfg["tifpath"], l1ctol2a(product) + "_20m.tif"))
        df.loc[product, "L2Atif60"] = os.path.exists(
            join(cfg["tifpath"], l1ctol2a(product) + "_60m.tif"))

    pbar.finish()
    return df


def append_todos(df):

    for product, row in df.iterrows():
        # do sen2cor if L1C exists and no L2A
        #df.loc[product,"do_sen2cor"]=row["L1C"] and not row["L2A"]


        tifmissing=not row["L2Atif10"] or not row["L2Atif20"] or not row["L2Atif60"]

        # do sen2cor if L1C exists and at least one tif missing and the product is not empty 
        df.loc[product, "do_sen2cor"] = row["L1C"] and tifmissing and not row["nogranules"]

        # do crop L1C
        df.loc[product, "do_cropL1C"] = row["L1C"] and tifmissing and not row["nogranules"]

        # do crop L1C
        df.loc[product, "do_cropL2A"] = row["L2A"] and tifmissing and not row["nogranules"]

        # do download if not already downloaded (in L1C) and if not marked as nogranules
        df.loc[product, "do_download"] = not row["L1C"] and not row["nogranules"]

    return df


def write_status_and_todos(cfg, df):

    def write(products, filename):
        with open(filename, 'w') as f:
            for item in products:
                f.write("%s\n" % item)

    write(list(df[df['do_sen2cor']].index), join(cfg["path"], "sen2cor.todo"))
    write(list(df[df['do_cropL1C']].index), join(cfg["path"], "cropL1C.todo"))
    write(list(df[df['do_cropL2A']].index), join(cfg["path"], "cropL2A.todo"))
    write(list(df[df['do_download']].index), join(cfg["path"], "download.todo"))

    df.to_csv(join(cfg["path"], "status.csv"))


if __name__ == '__main__':
    main()
