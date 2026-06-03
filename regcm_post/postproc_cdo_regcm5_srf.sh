#!/bin/bash

#SBATCH -A CMPNS_ictpclim
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

EXP_LIST="exp2 exp3 exp12 exp25"
VAR_LIST="pr psl uas vas sfcWind"

echo
echo "--------------- INIT POSPROCESSING MODEL ----------------"

echo
echo "1. Select variable"
for EXP in ${EXP_LIST[@]}; do

	DIR_IN="/leonardo/home/userexternal/nchristi/scratch/SEA/${EXP}/output"
	DIR_OUT="/leonardo/home/userexternal/nchristi/sumatra_work/SEA/${EXP}"
	mkdir -p "${DIR_OUT}"

	echo
	cd ${DIR_IN}
	echo ${DIR_IN}

		for VAR in ${VAR_LIST[@]}; do
			CDO selname,${VAR} *SRF*.nc ${DIR_OUT}/${VAR}_SRF.nc
		done
done    

echo
echo "--------------- THE END POSPROCESSING MODEL ----------------"

}




