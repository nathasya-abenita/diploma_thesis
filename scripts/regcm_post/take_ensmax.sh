EXP_LIST="EC-Earth3-Veg  MPI-ESM1-2-HR  NorESM2-MM  tweak"
# EXP_LIST="factual"
echo
echo "--------------- INIT POSPROCESSING MODEL ----------------"

echo
echo "1. Select variable"
for EXP in ${EXP_LIST[@]}; do

	DIR_IN="/home/nathasya/Documents/diploma_thesis/data/final_exp/counterfactual/GWL-1.5/${EXP}"
    # DIR_IN="/home/nathasya/Documents/diploma_thesis/data/final_exp/${EXP}"

	echo
	cd ${DIR_IN}
	echo ${DIR_IN}

	tmpfiles=()

    for f in wa*_pycordex.nc; do
        var=$(cdo showname "$f" | xargs)
        tmp="tmp_$(basename "$f")"
        echo "$var"
        cdo -chname,"$var",wa -delete,timestep=1 "$f" "$tmp"

        tmpfiles+=("$tmp")
    done

    #cdo -O ensmax -timmax "${tmpfiles[@]}" wa_max.nc
    cdo -O ensmax "${tmpfiles[@]}" wa_max.nc

    rm -f "${tmpfiles[@]}"
done    