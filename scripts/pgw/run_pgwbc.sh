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

INPUT=/leonardo_work/ICT26_ESP/RCMDATA/
NAMELIST=RegCM5-ERA5.in
BINARIES=/leonardo/home/userexternal/nchristi/RegCM/bin
MODELS=("EC-Earth3-Veg") #("EC-Earth3-Veg"  "MPI-ESM1-2-HR"  "NorESM2-MM")

for MODEL in "${MODELS[@]}"; do
	NAMELIST=/leonardo/home/userexternal/nchristi/diploma_thesis/regcm_exp/counterfactual/
	$BINARIES/pgwbcCLM45 $NAMELIST $INPUT/$MODEL
	$BINARIES/pgw_icbcCLM45 $ICBC 
done
}
