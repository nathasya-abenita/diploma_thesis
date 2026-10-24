EXP_LIST="EC-Earth3-Veg  MPI-ESM1-2-HR  NorESM2-MM"
#EXP_LIST="factual"

levels=(1000 925 850 700)

echo
echo "--------------- INIT POSPROCESSING MODEL ----------------"

echo
echo "1. Select variable"
for EXP in ${EXP_LIST[@]}; do

	DIR_IN="/leonardo/home/userexternal/nchristi/post_temp/cfac/GWL+3.0/${EXP}"
	DIR_FAC="/leonardo/home/userexternal/nchristi/post/fac"
	file="ts_ICBC.nc"
	
	cd ${DIR_IN}
	echo ${DIR_IN}
	cdo sub -selvar,ts ${file} -selvar,ts ${DIR_FAC}/${file} delta_ts.nc 
done    
