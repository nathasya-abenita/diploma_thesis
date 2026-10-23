#!/bin/bash

#SBATCH -A ICT26_ESP
#SBATCH -p dcgp_usr_prod
#SBATCH -N 1
#SBATCH --ntasks-per-node=112
#SBATCH -t 1-00:00:00
#SBATCH -o logs/run_pgwbc.out
#SBATCH -e logs/run_pgwbc.err
#SBATCH -J pgw
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=nchristi@ictp.it

{
set -eo pipefail
source /leonardo/home/userexternal/nchristi/modules_new

FAC_INP_PATH=/leonardo/home/userexternal/nchristi/scratch/final/fac/input
INPUT=/leonardo_work/ICT26_ESP/RCMDATA/PGW
NAMELIST=RegCM5-ERA5.in
BINARIES=/leonardo/home/userexternal/nchristi/RegCM/bin
MODELS="MPI-ESM1-2-HR NorESM2-MM"
#"EC-Earth3-Veg MPI-ESM1-2-HR NorESM2-MM"
GWL="GWL+3.0"
CFAC_PATH="/leonardo/home/userexternal/nchristi/scratch/final/cfac/$GWL"

for MODEL in ${MODELS[@]}; do
	# Change directory and copy ICBC from factual
	echo $CFAC_PATH/$MODEL/input
	cd $CFAC_PATH/$MODEL/input
	cp -rn $FAC_INP_PATH/* .

	# Define counterfactual namelist (cordex mode)  path
	CFAC_IN=/leonardo/home/userexternal/nchristi/diploma_thesis/regcm_exp/cfac/$GWL/$MODEL/cordex/RegCM5-ERA5.in
	# Execute PGW method from RegCM5
	echo $CFAC_IN
	$BINARIES/pgwbcCLM45 $CFAC_IN $INPUT/$MODEL/*GWL3.0*
	$BINARIES/pgw_icbcCLM45 *ICBC*.nc *PGWBC*.nc 
done
}
