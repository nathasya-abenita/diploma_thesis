import numpy as np
import xarray as xr
import os

def complete_path(filename, folder_path):
    return os.path.join(folder_path, filename)

if __name__ == '__main__':
    exp_list = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']
    #folder_path_list = ['/leonardo/home/userexternal/nchristi/post/fac']
    folder_path_list = [f'/leonardo/home/userexternal/nchristi/post_temp/cfac/GWL+1.5/{exp}' for exp in exp_list] # note that we're defining this now as the start, not factual folder
    folder_path_list += [f'/leonardo/home/userexternal/nchristi/post_temp/cfac/GWL-1.5/{exp}' for exp in exp_list]

    for folder_path in folder_path_list:
        print('assessing:', folder_path)

        # Pressure levels (Pa)
        levels = [1000, 925, 850, 700]
        pressure = np.array(levels) * 100.0

        # Gravity (m s^-2)
        g = 9.8

        # Read q*u and q*v
        qu = xr.concat(
            [xr.open_dataset(complete_path(f"qu{lev}.nc", folder_path))["qu"] for lev in levels],
            dim="pressure"
        ).assign_coords(pressure=pressure)

        qv = xr.concat(
            [xr.open_dataset(complete_path(f"qv{lev}.nc", folder_path))["qv"] for lev in levels],
            dim="pressure"
        ).assign_coords(pressure=pressure)

        # Ensure pressure is increasing before integration
        qu = qu.sortby("pressure")
        qv = qv.sortby("pressure")

        # Vertical integration
        ivtu = qu.integrate("pressure") / g
        ivtv = qv.integrate("pressure") / g

        # Magnitude
        ivt = np.hypot(ivtu, ivtv)

        # Save
        ds_out = xr.Dataset(
            {
                "ivtu": ivtu,
                "ivtv": ivtv,
                "ivt": ivt,
            }
        )

        ds_out["ivtu"].attrs.update({
            "long_name": "Integrated zonal water vapor transport",
            "units": "kg m-1 s-1"
        })

        ds_out["ivtv"].attrs.update({
            "long_name": "Integrated meridional water vapor transport",
            "units": "kg m-1 s-1"
        })

        ds_out["ivt"].attrs.update({
            "long_name": "Integrated water vapor transport magnitude",
            "units": "kg m-1 s-1"
        })

        ds_out.to_netcdf(complete_path("ivt_1000_700.nc", folder_path))
