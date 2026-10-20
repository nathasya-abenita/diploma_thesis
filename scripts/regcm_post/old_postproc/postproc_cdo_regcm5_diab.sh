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

#EXP_LIST="EC-Earth3-Veg  MPI-ESM1-2-HR  NorESM2-MM  tweak"
EXP_LIST="fin_diag"
VAR_LIST="ttenlsc"

LON_MIN=90
LON_MAX=115
LAT_MIN=-5
LAT_MAX=15

echo
echo "--------------- INIT POSPROCESSING MODEL ----------------"

echo
echo "1. Select variable"
for EXP in ${EXP_LIST[@]}; do
	
	#DIR_IN="/leonardo/home/userexternal/nchristi/scratch/counterfactual_diag/GWL-1.5/${EXP}/output"
	#DIR_OUT="/leonardo/home/userexternal/nchristi/sumatra_work/counterfactual/GWL-1.5/${EXP}"
	DIR_IN="/leonardo/home/userexternal/nchristi/scratch/factual/${EXP}"
        DIR_OUT="/leonardo/home/userexternal/nchristi/sumatra_work/factual/fin"
	mkdir -p "${DIR_OUT}"

	echo
	cd ${DIR_IN}
	echo ${DIR_IN}

		for VAR in ${VAR_LIST[@]}; do
			CDO vertmax -sellonlatbox,\
${LON_MIN},${LON_MAX},${LAT_MIN},${LAT_MAX} \
			-selname,${VAR} *ATM*.nc ${DIR_OUT}/${VAR}_max.nc
		done
done    

echo
echo "--------------- THE END POSPROCESSING MODEL ----------------"

}




