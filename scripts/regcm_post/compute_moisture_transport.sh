EXP_LIST="EC-Earth3-Veg  MPI-ESM1-2-HR  NorESM2-MM  tweak"
# EXP_LIST="factual"

levels=(1000 925 850 700)

echo
echo "--------------- INIT POSPROCESSING MODEL ----------------"

echo
echo "1. Select variable"
for EXP in ${EXP_LIST[@]}; do

	DIR_IN="/home/nathasya/Documents/diploma_thesis/data/final_exp/counterfactual/GWL+1.5/${EXP}"
    # DIR_IN="/home/nathasya/Documents/diploma_thesis/data/final_exp/${EXP}"

	echo
	cd ${DIR_IN}
	echo ${DIR_IN}

    for lev in "${levels[@]}"; do

        # Rename variables
        cdo chname,hus${lev},hus hus${lev}_pycordex.nc hus_tmp.nc
        cdo chname,ua${lev},ua ua${lev}_pycordex.nc ua_tmp.nc
        cdo chname,va${lev},va va${lev}_pycordex.nc va_tmp.nc

        # Compute products
        cdo mul hus_tmp.nc ua_tmp.nc qu${lev}.nc
        cdo mul hus_tmp.nc va_tmp.nc qv${lev}.nc

        # Rename output variables
        cdo chname,hus,qu qu${lev}.nc qu${lev}_tmp.nc
        mv qu${lev}_tmp.nc qu${lev}.nc

        cdo chname,hus,qv qv${lev}.nc qv${lev}_tmp.nc
        mv qv${lev}_tmp.nc qv${lev}.nc

        rm hus_tmp.nc ua_tmp.nc va_tmp.nc
    done
done    