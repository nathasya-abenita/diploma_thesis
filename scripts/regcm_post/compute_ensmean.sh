EXP_LIST="GWL+3.0 GWL-1.5 GWL+1.5"

for EXP in ${EXP_LIST[@]}; do
	echo ${EXP}

	DIR_IN="/leonardo/home/userexternal/nchristi/post_temp/cfac/${EXP}"
	
	cd ${DIR_IN}
	cdo ensmean */zg500_pycordex.nc zg500_ensmean.nc
	cdo daymean zg500_ensmean.nc zg500_ensmean_daily.nc	
done    
