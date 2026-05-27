#!/bin/bash

set -e

# User settings
YEAR=2025
MONTH=11

# Variable list
VARS=("geop" "qhum" "tatm" "uwnd" "vwnd")

INPUT_DIR="/leonardo/home/userexternal/nchristi/RCMDATA/ERA5/2025"
OUTPUT_DIR="/leonardo/home/userexternal/nchristi/sumatra_work/out"

# Domain
LON_MIN=80
LON_MAX=130
LAT_MIN=-15
LAT_MAX=15

# Date
START_DATE="2025-11-23"
END_DATE="2025-11-29"

# Create output directory
mkdir -p "${OUTPUT_DIR}"

for VARNAME in "${VARS[@]}"; do
    echo "Processing variable: ${VARNAME}"

    INPUT_FILE="${INPUT_DIR}/${VARNAME}_${YEAR}_${MONTH}.nc"
    FINAL_FILE="${OUTPUT_DIR}/${VARNAME}_Senyar.nc"

    if [ -f "${INPUT_FILE}" ]; then

        echo "Processing ${INPUT_FILE}"

        cdo seldate,${START_DATE},${END_DATE} \
            -sellonlatbox,\
${LON_MIN},${LON_MAX},${LAT_MIN},${LAT_MAX} \
            "${INPUT_FILE}" \
            "${FINAL_FILE}"


    else
        echo "WARNING: Missing file ${INPUT_FILE}"
    fi
    
done

# OPTIONAL CLEANUP
# rm -rf "${TMP_DIR}"

echo "All processing completed."