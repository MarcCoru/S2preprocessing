# Preprocessing Pipeline

Sentinel 2

Preprocessing steps
* query
* download
* atmospheric correction
* conversion to .tif
* upload to postgresql db DB

project emerged from thesis repository

## Installation

clone repository
```bash
git clone https://github.com/MarcCoru/S2preprocessing.git
sh setup.sh
```

## Dependencies

satellite data query
```
https://github.com/kraftek/awsdownload/releases/download/1.7/ProductDownload-1.7
```

satellite data download
```
https://github.com/sentinel-hub/sentinelhub-py
```

## Pipeline

##### Query available products from Amazon Web Service (AWS)

```bash
sh query.sh sites/munich.site
```

creates ```$queryfile``` containing product names

##### Download products from $queryfile

```bash
sh download.sh sites/munich.site
```

##### Optional: Delete unnecessary tiles to reduce file size and processing time

```bash
python delGranules.py sites/munich.site
```

Dry run flag ```-d``` only simulates deletion

```bash
python delGranules.py sites/munich.site -d
```


the config file must include a ```granules``` variable
e.g.
```bash
granules="32UPU 32UQU 33UTP 33UUP"
```

[Here](https://mappingsupport.com/p/coordinates-mgrs-google-maps.html) is an online tool to determine Granules

##### Atmospheric correction with Sen2Cor

```bash
sh sen2cor.sh sites/munich.site
```

The Sentinel 2 atomspheric correction config file ```L2A_GIPP.xml``` is by
default stored in the project root directory.
However, the location can be changed in the config file using the ```L2A_GIPP_path``` variable

## DB

addTrainEval site

Add a "is evaluate" column to a polygon dataset
```bash
sh addEvalField.sh sites/bavaria.site tiles eval "0.8" ""
```

Add a "is train" column to a polygon dataset (eval=1 are excluded)
```bash
sh addEvalField.sh sites/bavaria.site tiles train "0.75" "where eval=0"
```

# GDAL drivers must be enables:
enable via (as sudo user: ```$sudo -u postgres -d fields```)
```
SET postgis.gdal_enabled_drivers = 'ENABLE_ALL';
ALTER SYSTEM SET postgis.gdal_enabled_drivers TO 'GTiff PNG JPEG';
SELECT pg_reload_conf();
```

test if enabled via
```
SELECT short_name, long_name FROM ST_GDALDrivers();
```

### Sentinel 2 Bands
