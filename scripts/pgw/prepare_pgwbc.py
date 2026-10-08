import os
import re

# 1.1 Path to your template namelist and output directory for .in files
GWL_LABEL = '+3.0'
TEMPLATE_FILE = "./test/template.in"
NAMELIST_DIR = f"./test/regcm_exp/cfac/GWL{GWL_LABEL}" # to save namelists (regcm_exp folder)
SCRATCH_DIR = f"./test/scratch/final/fac/GWL{GWL_LABEL}" # input folder in scratch

# 1.2 Define GHG tweak ratios
'''
gas_tweak_factors = 1.5, 1.4 , 1.1 , 0.5 , 0.6,
!                   CO2  CH4   N2O   CFC11 CFC12
'''
if GWL_LABEL == '+3.0':
    ghg_tweak_ratio = "1.6, 1.5, 1.2, 0.4, 0.6"
elif GWL_LABEL == '+1.5':
    ghg_tweak_ratio = "1.1, 1.1, 1.0, 0.8, 0.9"
elif GWL_LABEL == '-1.5':
    ghg_tweak_ratio = "0.7, 0.5, 0.8, 0.0, 0.0"
else:
    raise ValueError ('unrecognized global warming level!')


# 2. Configuration list for CMIP6 models

cmip6_models = ['EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']

diag_mode = {
    "ifatm"     : ".true",
    "atmfrq"    : "3",
    "ifrad"     : ".false.",
    "ifsts"     : ".false.",
    "ifshf"     : ".false.",
    "ifsrf"     : ".false.",
    "idiag"     : "1",
    "ifcordex"  : ".false."
}

cordex_mode = {
    "atmfrq"    : "1",
    "ifatm"     : ".true",
    "atmfrq"    : "1",
    "ifrad"     : ".true.",
    "ifsts"     : ".true.",
    "ifshf"     : ".true.",
    "ifsrf"     : ".true.",
    "idiag"     : "0",
    "ifcordex"  : ".true."
}

cmip6_namelists = []
for model in cmip6_models:
    nl = {
        "dirter" : os.path.join(SCRATCH_DIR, 'input'),
        "dirglob" : os.path.join(SCRATCH_DIR, 'input'),
        "dirout" : os.path.join(SCRATCH_DIR, 'output')
    }
    cmip6_namelists.append(nl)

def replace_namelist_val(content, param_name, new_value):
    """Replace a parameter value in Fortran namelist syntax."""

    if isinstance(new_value, str):
        val_str = f"'{new_value}'"
    else:
        val_str = str(new_value)

    pattern = rf"({re.escape(param_name)}\s*=\s*)([^/\n!]+)"

    return re.sub(
        pattern,
        rf"\1{val_str}",
        content,
        flags=re.IGNORECASE,
    )

def main():
    if not os.path.exists(TEMPLATE_FILE):
        print(f"Error: Template '{TEMPLATE_FILE}' not found!")
        return
    
    with open(TEMPLATE_FILE, "r") as f:
        template_content = f.read()

    for model_name, m in zip(cmip6_models, cmip6_namelists):
        content = template_content
        
        # Replace model-specific parameters and paths
        for parameter, value in m.items():
            content = replace_namelist_val(content, parameter, value)

        # Create output directories if they don't exist
        os.makedirs(m["dirglob"], exist_ok=True)
        os.makedirs(m["dirout"], exist_ok=True)
        os.makedirs(os.path.join(NAMELIST_DIR, model_name, 'cordex'))
        os.makedirs(os.path.join(NAMELIST_DIR, model_name, 'diag'))

        # Replace output for diagnostic mode
        for parameter, value in diag_mode.items():
            content = replace_namelist_val(content, parameter, value)

        # Save to individual namelist file
        out_path = os.path.join(NAMELIST_DIR, model_name, 'diag', "RegCM5-ERA5.in")
        with open(out_path, "w") as f:
            f.write(content)

        # Replace output for diagnostic mode
        for parameter, value in diag_mode.items():
            content = replace_namelist_val(content, parameter, value)

        # Save to individual namelist file
        out_path = os.path.join(NAMELIST_DIR, model_name, 'cordex', "RegCM5-ERA5.in")
        with open(out_path, "w") as f:
            f.write(content)

        print(f"Successfully generated: {out_path}")

if __name__ == "__main__":
    main()