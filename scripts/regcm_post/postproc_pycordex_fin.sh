#!/bin/bash

#SBATCH -A ICT26_ESP
#SBATCH -p dcgp_usr_prod
#SBATCH -N 1
#SBATCH --ntasks-per-node=112
#SBATCH -t 1-00:00:00
#SBATCH -J postproc
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=nchristi@ictp.it

{
set -eo pipefail

CDO(){
  cdo -O -L -f nc4 -z zip $@
}

EXP_LIST="fin"
#EXP_LIST="EC-Earth3-Veg  MPI-ESM1-2-HR  NorESM2-MM  tweak"
VAR_LIST="ua va wa zg hus"
LEV_LIST="1000 925 850 700 600 500"

LON_MIN=90
LON_MAX=115
LAT_MIN=-5
LAT_MAX=15

CORDEX_PATH="CORDEX-CMIP6/DD/exp_senyar-4/ICTP/ERA5/evaluation/r1i1p1f1/RegCM5-0/v1-r1/6hr"

echo
echo "--------------- INIT POSPROCESSING MODEL ----------------"

echo
echo "1. Select variable"
for EXP in ${EXP_LIST[@]}; do
	
	#DIR_IN="/leonardo/home/userexternal/nchristi/scratch/counterfactual/GWL+1.5/${EXP}/output/${CORDEX_PATH}"
	DIR_IN="/leonardo/home/userexternal/nchristi/scratch/factual/${EXP}/${CORDEX_PATH}"
	#DIR_OUT="/leonardo/home/userexternal/nchristi/sumatra_work/counterfactual/GWL+1.5/${EXP}"
	DIR_OUT="/leonardo/home/userexternal/nchristi/sumatra_work/factual/${EXP}"
	mkdir -p "${DIR_OUT}"

	echo
	cd ${DIR_IN}
	echo ${DIR_IN}

		for VAR in ${VAR_LIST[@]}; do
			for LEV in ${LEV_LIST[@]}; do
				CDO sellonlatbox,${LON_MIN},${LON_MAX},${LAT_MIN},${LAT_MAX} -selname,${VAR}${LEV} *${VAR}${LEV}/*.nc ${DIR_OUT}/${VAR}${LEV}_pycordex.nc
			done
		done
done    

echo
echo "--------------- THE END POSPROCESSING MODEL ----------------"

}




