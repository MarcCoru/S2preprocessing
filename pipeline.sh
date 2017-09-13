#!/bin/bash

cfg_path=$1

sh query.sh $cfg_path
sh download.sh $cfg_path

sh warp.sh $cfg_path L1C
