#!/bin/bash

#SBATCH -A ICT26_ESP
#SBATCH -p dcgp_usr_prod
#SBATCH -N 2
#SBATCH --ntasks-per-node=112
#SBATCH -t 1-00:00:00
#SBATCH -J Plot
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=nchristi@ictp.it
#SBATCH -o logs/plots.out

{
set -eo pipefail
python pgw/final/plot_perturbation.py
python pgw/final/plot_tas.py
}
