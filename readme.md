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
```
git clone git@gitlab.lrz.de:ga73yox/preprocessing.git
sh setup.sh
```

## Pipeline

### Deletion of granules outside of AOI

```
sh query.sh ./bavaria.cfg
```

delete unnecessary granules (for faster sen2cor) -d flag for dry run
```
python delGranules.py ./test.cfg -d
```

```
sh sen2cor.sh ./test.cfg
```
