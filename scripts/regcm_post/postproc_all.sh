#!/bin/bash

#SBATCH -A ICT26_ESP
#SBATCH -p dcgp_usr_prod
#SBATCH -N 1
#SBATCH --ntasks-per-node=112
#SBATCH -t 1-00:00:00
#SBATCH -J postproc
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=nchristi@ictp.it
#SBATCH -o logs/postproc.out
#SBATCH -e logs/postproc.err
{
set -eo pipefail

CDO(){
  cdo -O -L -f nc4 -z zip $@
}

#EXP_LIST="tweak"
EXP_LIST="EC-Earth3-Veg  MPI-ESM1-2-HR  NorESM2-MM"
VAR_CORDEX_LIST="ua va zg hus"
VAR_SRF_LIST="pr psl sfcWind uas vas tas cape cin evspsbl"
VAR_ATM_LIST="ttenlsc wa"
VAR_IN_LIST="ts"
LEV_LIST="1000 925 850 700 600 500 400 300 250 200"

LON_MIN=90
LON_MAX=115
LAT_MIN=-5
LAT_MAX=15

CORDEX_PATH="CORDEX-CMIP6/DD/exp_senyar-4/ICTP/ERA5/evaluation/r1i1p1f1/RegCM5-0/v1-r1/3hr"

echo
echo "--------------- INIT POSPROCESSING MODEL ----------------"

echo
echo "1. Select variable"
for EXP in ${EXP_LIST[@]}; do
	
	DIR_IN="/leonardo/home/userexternal/nchristi/scratch/final/cfac/GWL+3.0/${EXP}/output/cordex"
	DIR_OUT="/leonardo/home/userexternal/nchristi/post/cfac/GWL+3.0/${EXP}"

	#DIR_IN="/leonardo/home/userexternal/nchristi/scratch/final/fac/output/cordex"
	#DIR_OUT="/leonardo/home/userexternal/nchristi/post/fac"

	mkdir -p "${DIR_OUT}"

	echo
	cd ${DIR_IN}
	echo ${DIR_IN}

	# Handle SRF variables
	for VAR in ${VAR_SRF_LIST[@]}; do
		CDO sellonlatbox,${LON_MIN},${LON_MAX},${LAT_MIN},${LAT_MAX} -selname,${VAR} *SRF*.nc ${DIR_OUT}/${VAR}_SRF.nc
	done
	
	# Handle ICBC variables
	cd "../../input"
	for VAR in ${VAR_IN_LIST[@]}; do
                CDO sellonlatbox,${LON_MIN},${LON_MAX},${LAT_MIN},${LAT_MAX} -selname,${VAR} *ICBC*.nc ${DIR_OUT}/${VAR}_ICBC.nc
        done

	# Handle vertical max of ATM variables
	cd "../output/diag"
	for VAR in ${VAR_ATM_LIST[@]}; do
		CDO vertmax -sellonlatbox,${LON_MIN},${LON_MAX},${LAT_MIN},${LAT_MAX} -selname,${VAR} *ATM*.nc ${DIR_OUT}/${VAR}_max.nc
	done

	# Handle CORDEX-derived variables
	cd "../cordex/${CORDEX_PATH}"
	for VAR in ${VAR_CORDEX_LIST[@]}; do
		for LEV in ${LEV_LIST[@]}; do
			CDO sellonlatbox,${LON_MIN},${LON_MAX},${LAT_MIN},${LAT_MAX} -selname,${VAR}${LEV} *${VAR}${LEV}/*.nc ${DIR_OUT}/${VAR}${LEV}_pycordex.nc
		done
	done
done    

echo
echo "--------------- THE END POSPROCESSING MODEL ----------------"

}




