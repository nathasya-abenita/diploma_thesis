#!/bin/bash

#SBATCH -A ICT26_ESP
#SBATCH -p dcgp_usr_prod
#SBATCH -N 1
#SBATCH --ntasks-per-node=112
#SBATCH -t 1-00:00:00
#SBATCH -J compute_delta
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=nchristi@ictp.it

shopt -s nullglob

LON1=85
LON2=120
LAT1=-10
LAT2=20

HIST_DIR="/leonardo/home/userexternal/nchristi/Natha/CMIP6/historical"
SSP_DIR="/leonardo/home/userexternal/nchristi/Natha/CMIP6/ssp245"
OUT_DIR="/leonardo/home/userexternal/nchristi/sumatra_work/pgw"

YEAR_HIST_START=1850
YEAR_HIST_END=1879
YEAR_SSP_START=2010
YEAR_SSP_END=2049

variables=( 'hus' 'ta' 'ts' )

models=( 'AWI-CM-1-1-MR' 'CESM2-WACCM' 'EC-Earth3' 'FGOALS-g3' 'GISS-E2-1-G' 'GISS-E2-1-H' 'INM-CM4-8' 'INM-CM5-0' 'IPSL-CM6A-LR' 'MCM-UA-1-0' 'MIROC6' 'MIROC-ES2L' 'MRI-ESM2-0' 'NorESM2-LM' 'NorESM2-MM' )

for model in "${models[@]}"; do

    echo "========================================"
    echo "Model: ${model}"

    mkdir -p "${OUT_DIR}/${model}"

    for var in "${variables[@]}"; do

        echo "  Variable: ${var}"
	
	#echo "HIST:"
	#printf '%s\n' "${HIST_DIR}/${model}/${var}_"*historical*.nc
	#echo "SSP:"
	#printf '%s\n' "${SSP_DIR}/${model}/${var}_"*ssp*.nc

        files=( "${HIST_DIR}/${model}/${var}_"*historical*.nc )
	files+=( "${SSP_DIR}/${model}/${var}_"*ssp*.nc )
	#echo "${files[@]}"

        #if [ -z "${files[@]}" ]; then
        #    echo "    No files found."
        #    continue
    	#fi

	outfile1="${OUT_DIR}/${model}/${var}_nov_hist.nc"
        outfile2="${OUT_DIR}/${model}/${var}_nov_ssp.nc"
	outfile="${OUT_DIR}/${model}/${var}_nov_delta.nc"

        tmpfile="${OUT_DIR}/${model}/${var}_merged.nc"

        #cdo -L sellonlatbox,${LON1},${LON2},${LAT1},${LAT2} -mergetime "${files[@]}" "$tmpfile"


        # ---------------------------------------------
        # Check year coverage
        # ---------------------------------------------
        years=$(cdo -s showyear "$tmpfile")

        missing=()

        for ((y=YEAR_HIST_START; y<=YEAR_HIST_END; y++)); do
            if ! grep -qw "$y" <<< "$years"; then
                missing+=("$y")
            fi
        done

        if [ ${#missing[@]} -eq 0 ]; then
		echo "    Year coverage: OK (${YEAR_HIST_START}-${YEAR_HIST_END})"
        else
            echo "    Missing years: ${missing[*]}"
        fi
	
	missing=()

        for ((y=YEAR_SSP_START; y<=YEAR_SSP_END; y++)); do
            if ! grep -qw "$y" <<< "$years"; then
                missing+=("$y")
            fi
        done

        if [ ${#missing[@]} -eq 0 ]; then
            echo "    Year coverage: OK (${YEAR_SSP_START}-${YEAR_SSP_END})"
        else
            echo "    Missing years: ${missing[*]}"
        fi

        # ---------------------------------------------
        # November climatology
        # ---------------------------------------------
	#cdo -L timmean -selmon,11 -selyear,${YEAR_HIST_START}/${YEAR_HIST_END} "$tmpfile" "$outfile1"

	#cdo -L timmean -selmon,11 -selyear,${YEAR_SSP_START}/${YEAR_SSP_END} "$tmpfile" "$outfile2"

	cdo sub "$outfile1" "$outfile2" "$outfile"
    done

done
