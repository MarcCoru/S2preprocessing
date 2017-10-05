import json
import subprocess
import argparse
import os
import sys

"""
Takes Sentinel 2 Product file and creates 10m, 20m and 60m VRT files in a predefined order
"""

def main():

    parser = argparse.ArgumentParser(description='adds VRT bands to Sentinel SAFE images for easier data handling')
    parser.add_argument('product', type=str,
                        help='product path (to SAFE file)')
    parser.add_argument('--bandconfigfile', default=None,
                        help='config json file for band sequences')

    parser.add_argument('--gdalbuildvrt', default="gdalbuildvrt",
                        help='path to gdalbuildvrt program. Defaults to program defined in PATH')

    parser.add_argument('--verbose', action='store_true',
                            help='display additional text')

    args = parser.parse_args()

    if not os.path.exists(args.product):
        print "No folder found unter product path. Exit"
        sys.exit()


    # set bandconfig default
    if args.bandconfigfile is None:
        args.bandconfig = json.loads("""
        {
          "L1C": {
            "10m": ["B04","B03","B02","B08"],
            "20m": ["B05","B06","B07","B8A","B11","B12"],
            "60m": ["B01","B09","B10"]
          },
          "L2A": {
            "10m" : ["B04","B03","B02","B08"],
            "20m" : ["B05","B06","B07","B8A","B11","B12","AOT","CLD","SCL","SNW","WVP"],
            "60m" : ["B01","B09"]
          }
        }
        """)
    else:
        with open(args.bandconfigfile) as data_file:
            args.bandconfig = json.load(data_file)

    addVRTs(args)

def addVRTs(args):

    bandcfg = args.bandconfig

    # "/home/russwurm/projects/preprocessing/conda/bin/gdalbuildvrt"
    buildvrtcommand=args.gdalbuildvrt

    #product="fails/S2A_MSIL2A_20170223T101021_N0204_R022_T32UQU_20170223T101550.SAFE"
    #level="L2A"

    #product="works/S2A_USER_PRD_MSIL2A_PDMC_20161115T190806_R022_V20161115T101302_20161115T101302.SAFE"
    #level="L2A"

    if "L1C" in args.product.split('/')[-1]:
        level="L1C"
    elif "L2A" in args.product.split('/')[-1]:
        level="L2A"

    product=args.product

    #product="fails/S2A_MSIL1C_20170223T101021_N0204_R022_T32UQU_20170223T101550.SAFE"
    #level="L1C"

    if not os.path.exists(os.path.join(args.product,"vrt")):
        os.makedirs(os.path.join(args.product,"vrt"))

    def createvrt(product,band,resolution,level):
        if level=="L2A": # B01_10m.jp2
            bashCommand = "find {product} -name *{band}*{res}.jp2".format(product=product, band=band, res=resolution)
        if level=="L1C": # B01.jp2
            bashCommand = "find {product} -name *{band}.jp2".format(product=product, band=band)

        if args.verbose: print bashCommand

        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        images = output.split('\n')

        bashCommand = "{gdalbuildvrt} {product}/vrt/{band}_{res}.vrt {images}".format(gdalbuildvrt=buildvrtcommand,
                                                                            product=product, band=band,res=resolution,
                                                                            images=' '.join(images))
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        return process.communicate()

    for resolution in bandcfg[level].keys():

        bands = bandcfg[level][resolution]

        # build vrt for each band
        for band in bands:

            # create one vrt for each band
            createvrt(product,band,resolution,level)

        # merge bands to resolution vrts

        bandvrts=" ".join(["{product}/vrt/{band}_{res}.vrt".format(product=product,band=b,res=resolution) for b in bands]) # B02.vrt B03.vrt B04.vrt B08.vrt AOT.vrt WVP.vrt

        # bandarguments # e.g.
        bandarg=" ".join(["-b {}".format(b+1) for b in range(len(bands))]) # '-b 1 -b 2 -b 3 -b 4 -b 5 -b 6'

        # merge bands in proper sequence for 10m.vrt
        bashCommand = "{gdalbuildvrt} -separate {bandarg} {product}/{resolution}.vrt {bandvrts}".format(gdalbuildvrt=buildvrtcommand,
                                                                                                        bandarg=bandarg,
                                                                                                        product=product,
                                                                                                        bandvrts=bandvrts,
                                                                                                        resolution=resolution)

        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output,error=process.communicate()

if __name__ == "__main__":
    main()
