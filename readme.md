# Preprocessing Pipeline

Sentinel 2

Preprocessing steps
* query
* download
* atmospheric correction
* conversion to .tif (tbd)
* upload to DB (tbd)

project emerged from thesis repository

## Installation

clone repository
```bash
$git clone git@gitlab.lrz.de:ga73yox/preprocessing.git
$sh setup.sh
```

## Pipeline

##### Query available products from Amazon Web Service (AWS)

```bash
$sh query.sh sites/munich.site
```

creates ```$queryfile``` containing product names

##### Download products from $queryfile

```bash
$sh download.sh sites/munich.site
```

##### Optional: Delete unnecessary tiles to reduce file size and processing time

```bash
$python delGranules.py sites/munich.site
```

Dry run flag ```-d``` only simulates deletion

```bash
 $python delGranules.py sites/munich.site -d
 ```


the config file must include a ```granules``` variable
e.g.
```bash
granules="32UPU 32UQU 33UTP 33UUP"
```

[Here](https://mappingsupport.com/p/coordinates-mgrs-google-maps.html) is an online tool to determine Granules

##### Atmospheric correction with Sen2Cor

```bash
$sh sen2cor.sh sites/munich.site
```

The Sentinel 2 atomspheric correction config file ```L2A_GIPP.xml``` is by
default stored in the project root directory.
However, the location can be changed in the config file using the ```L2A_GIPP_path``` variable
