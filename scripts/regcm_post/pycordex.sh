#!/bin/bash

#SBATCH -A ICT26_ESP
#SBATCH -p dcgp_usr_prod
#SBATCH -N 2
#SBATCH --ntasks-per-node=112
#SBATCH -t 1-00:00:00
#SBATCH -o logs/pycordex.out
#SBATCH -e logs/pycordex.err
#SBATCH -J pycordex
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=nchristi@ictp.it

{
set -eo pipefail
source /leonardo/home/userexternal/nchristi/modules_new

PROGRAM=/leonardo/home/userexternal/ggiulian/RegCM-CORDEX5/Tools/Scripts/pycordexer/pycordexer.py

#OUTPUT_DIR=/leonardo/home/userexternal/nchristi/scratch/final/fac/output/cordex
#cd $OUTPUT_DIR
#$PROGRAM -m nchristi@ictp.it -d exp_senyar-4 -g ERA5 -e evaluation -b r1i1p1f1 -n None -o . --regcm-model-name RegCM -r 5.0 --regcm-version-id v1-r1 exp_senyar-4_ATM.2025112500.nc hus,ua,va,zg

MODELS=("EC-Earth3-Veg" "MPI-ESM1-2-HR" "NorESM2-MM")
#("EC-Earth3-Veg"  "MPI-ESM1-2-HR"  "NorESM2-MM" "tweak")
for MODEL in "${MODELS[@]}"; do
	OUTPUT_DIR=/leonardo/home/userexternal/nchristi/scratch/final/cfac/GWL+3.0/$MODEL/output/cordex
	cd $OUTPUT_DIR
	echo $OUTPUT_DIR
 	$PROGRAM -m nchristi@ictp.it -d exp_senyar-4 -g ERA5 -e evaluation -b r1i1p1f1 -n None -o . --regcm-model-name RegCM -r 5.0 --regcm-version-id v1-r1 exp_senyar-4_ATM.2025112500.nc hus,ua,va,zg
done
}
