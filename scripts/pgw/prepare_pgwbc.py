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
    ghg_tweak_ratio = [1.6, 1.5, 1.2, 0.4, 0.6]
elif GWL_LABEL == '+1.5':
    ghg_tweak_ratio = [1.1, 1.1, 1.0, 0.8, 0.9]
elif GWL_LABEL == '-1.5':
    ghg_tweak_ratio = [0.7, 0.5, 0.8, 0.0, 0.0]
else:
    raise ValueError ('unrecognized global warming level!')


# 2. Configuration list for CMIP6 models

cmip6_models = ['EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']

diag_mode = {
    "ifatm"     : True,
    "atmfrq"    : 3,
    "ifrad"     : False,
    "ifsts"     : False,
    "ifshf"     : False,
    "ifsrf"     : False,
    "idiag"     : 1,
    "ifcordex"  : False
}

cordex_mode = {
    "atmfrq"    : 1,
    "ifatm"     : True,
    "atmfrq"    : 1,
    "ifrad"     : True,
    "ifsts"     : True,
    "ifshf"     : True,
    "ifsrf"     : True,
    "idiag"     : 0,
    "ifcordex"  : True
}

cmip6_namelists = []
for model in cmip6_models:
    nl = {
        "dirter" : os.path.join(SCRATCH_DIR, 'input'),
        "dirglob" : os.path.join(SCRATCH_DIR, 'input'),
        "dirout" : os.path.join(SCRATCH_DIR, 'output')
    }
    cmip6_namelists.append(nl)

def format_namelist_value(value):
    """Convert a Python value to Fortran namelist syntax."""

    if isinstance(value, bool):
        return ".true." if value else ".false."

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        return str(value)

    if isinstance(value, (list, tuple)):
        return ", ".join(format_namelist_value(v) for v in value)

    if isinstance(value, str):
        return f"'{value}'"

    raise TypeError(f"Unsupported value type: {type(value)}")


def replace_namelist_val(content, param_name, new_value):
    """Replace a parameter value in a Fortran namelist."""

    val_str = format_namelist_value(new_value)

    pattern = (
        rf"(^\s*{re.escape(param_name)}\s*=\s*)"
        rf"(.*?)"
        rf"(,\s*(?:!.*)?$)"
    )

    return re.sub(
        pattern,
        rf"\g<1>{val_str}\g<3>",
        content,
        flags=re.IGNORECASE | re.MULTILINE,
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

        # Replace GHG tweak
        content = replace_namelist_val(content, 'gas_tweak_factors', ghg_tweak_ratio)

        # Replace output for diagnostic mode
        for parameter, value in diag_mode.items():
            content = replace_namelist_val(content, parameter, value)

        # Save to individual namelist file
        out_path = os.path.join(NAMELIST_DIR, model_name, 'diag', "RegCM5-ERA5.in")
        with open(out_path, "w") as f:
            f.write(content)

        # Replace output for cordex mode
        for parameter, value in cordex_mode.items():
            content = replace_namelist_val(content, parameter, value)

        # Save to individual namelist file
        out_path = os.path.join(NAMELIST_DIR, model_name, 'cordex', "RegCM5-ERA5.in")
        with open(out_path, "w") as f:
            f.write(content)

        print(f"Successfully generated: {out_path}")

if __name__ == "__main__":
    main()