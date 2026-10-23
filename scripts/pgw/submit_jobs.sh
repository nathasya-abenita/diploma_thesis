#!/bin/bash
# ==============================================================================
# Script to automate Slurm job submissions across multiple model subdirectories
# (e.g., cordex and diag subfolders per CMIP6 model)
# ==============================================================================

set -euo pipefail

# 1. Define the name of the Slurm job file present in each target directory
JOB_FILE="/leonardo/home/userexternal/nchristi/diploma_thesis/scripts/pgw/model.job"

# 2. Define the list of model directories
MODELS=(
    "EC-Earth3-Veg"
    "MPI-ESM1-2-HR" 
    "NorESM2-MM"
)

# 3. Define the subdirectories to process for each model
SUBDIRS=(
    "cordex"
)
#("cordex" "diag")

# Store the root execution directory (update this path if located elsewhere)
ROOT_DIR="/leonardo/home/userexternal/nchristi/diploma_thesis/regcm_exp/cfac/GWL+3.0"

echo "========================================================"
echo " Starting Slurm batch job submission across directories "
echo "========================================================"

for model in "${MODELS[@]}"; do
    for sub in "${SUBDIRS[@]}"; do
        TARGET_DIR="${ROOT_DIR}/${model}/${sub}"

        echo ""
        echo "--------------------------------------------------------"
        echo "Processing directory: ${model}/${sub}"
        echo "--------------------------------------------------------"

        if [ ! -d "${TARGET_DIR}" ]; then
            echo "WARNING: Directory '${TARGET_DIR}' does not exist. Skipping."
            continue
        fi

        # Execute inside a subshell to safely isolate directory changes
        (
            cd "${TARGET_DIR}"

            # Ensure the logs directory exists (required by #SBATCH -o logs/... and #SBATCH -e logs/...)
            mkdir -p logs

            if [ -f "${JOB_FILE}" ]; then
                echo "Submitting ${JOB_FILE} in $(pwd)..."
                sbatch "${JOB_FILE}"
            else
                echo "ERROR: Job file '${JOB_FILE}' not found in $(pwd)!"
                exit 1
            fi
        )
    done
done

echo ""
echo "========================================================"
echo " All job submissions processed successfully. "
echo "========================================================"
