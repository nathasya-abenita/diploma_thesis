#!/bin/bash

set -e

YEAR=2025
MONTH=11

# Variable list
VARS=("tatm" "uwnd" "vwnd")

INPUT_DIR="/leonardo/home/userexternal/nchristi/sumatra_work/out/era5"
OUTPUT_DIR="../data"

for VARNAME in "${VARS[@]}"; do

    FILENAME="${VARNAME}_Senyar.nc"
    scp "nchristi@login01-ext.leonardo.cineca.it:${INPUT_DIR}/${FILENAME}" "${OUTPUT_DIR}/${FILENAME}"
done

echo "All processing completed."