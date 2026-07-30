import os
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import warnings
warnings.filterwarnings('ignore')


# MAP_EXTENT =  [90, 115, -5, 14]
MAP_EXTENT =  [94, 108, -2, 7.5]

# Titles should be in respect with experiments name, excludin
EXPERIMENTS = ['factual', 'counterfactual/GWL-1.5/tweak',
               'counterfactual/GWL-1.5/EC-Earth3-Veg', 
               'counterfactual/GWL-1.5/MPI-ESM1-2-HR',
               'counterfactual/GWL-1.5/NorESM2-MM']
titles = ['MSWEP', 'factual', 'counterfactual/tweak', 'counterfactual/EC-Earth3-Veg', 'counterfactual/MPI-ESM1-2-HR', 'counterfactual/NorESM2-MM']

START_DATE = "2025-11-25 00:00:00"
END_DATE   = "2025-11-28 23:00:00"

# Paths
DATA_DIR_MODELS = ('./data/final_exp')
DATA_DIR_SAT = ('./data/sat/MSWEP/daily')
OUTPUT_PATH = ('./figs/compare')
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Functions
def fix_longitude(ds):

    if np.any(ds.lon > 180):
        ds['lon'] = (ds.lon + 180) % 360 - 180
        ds = ds.sortby('lon')

    return ds


def load_sat():

    nc_file = os.path.join(
        DATA_DIR_SAT,
        "daily.nc"
    )

    ds = xr.open_dataset(nc_file)
    ds = fix_longitude(ds)
    ds = ds.sel(time=slice(START_DATE, END_DATE))

    pr_acc = ds['precipitation'].sum(dim='time')

    return pr_acc


def load_model(exp):

    file_name = os.path.join(
        DATA_DIR_MODELS,
        exp,
        'pr_SRF.nc'
    )

    print(f'Opening {file_name}')

    ds = xr.open_dataset(file_name)
    ds = ds.rename({'xlon': 'lon', 'xlat': 'lat'})
    ds = fix_longitude(ds)
    ds = ds.sel(time=slice(START_DATE, END_DATE))

    pr_acc = ds['pr'].sum(dim='time') * 3600.

    return pr_acc

def load_stat ():
    # Define path to station data
    station_path = r'./data/senyar_station.nc'

    # Read file
    ds_stat = xr.open_dataset(station_path)

    # Slice time and take sum
    pr_stat = ds_stat['RR'].sel(time=slice(START_DATE, END_DATE))
    pr_stat = pr_stat.sum(dim='time')
    df_stat = pr_stat.to_dataframe()
    return df_stat

if __name__ == '__main__':
    # Load data
    df_stat = load_stat()
    all_precip = {}

    all_precip["MSWEP"] = load_sat()

    for exp in EXPERIMENTS:
        print(f"Loading {exp}...")
        pr_acc = load_model(exp)
        all_precip[exp.upper()] = pr_acc

    # Plot
    print("Plotting")
    fig, axes = plt.subplots(2, 3, figsize=(14, 9), subplot_kw={'projection': ccrs.PlateCarree()})
    axes = axes.flatten()

    levels = np.arange(0, 720, 5)
    base = plt.cm.terrain_r(np.linspace(0, 1, len(levels)-1))
    base[0] = [1, 1, 1, 1]
    cmap = mcolors.ListedColormap(base)
    norm = mcolors.BoundaryNorm(levels, ncolors=cmap.N + 1, extend='max')

    
    labels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)']

    for i, name in enumerate(titles):

        ax = axes[i]
        if name == 'MSWEP':
            pr = all_precip[name]
        else:
            pr = all_precip[EXPERIMENTS[i-1].upper()]
        cf = ax.contourf(pr.lon, pr.lat, pr, levels=levels, cmap=cmap, extend='max', transform=ccrs.PlateCarree())

        ax.set_extent(MAP_EXTENT)
        ax.coastlines(linewidth=0.75)
        ax.add_feature(cfeature.BORDERS, linewidth=0.75)

        gl = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', alpha=0.5)
        gl.top_labels = False
        gl.right_labels = False

        ax.set_title(f"{labels[i]} {name}", loc='left', fontsize=10, fontweight='bold')

    # Add station data
    axes[0].scatter(df_stat['longitude'], df_stat['latitude'], c=df_stat['RR'],
            cmap=cmap, vmin=levels.min(), vmax=levels.max(),
            edgecolors='k', label='station')
    axes[0].legend()
    
    # Colorbar
    cax = fig.add_axes([0.999, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(cf, cax=cax)
    cbar.set_label("Accumulated precipitation 25-28Nov2025 (mm)", fontsize=10, fontweight='bold')

    # Save figure
    print("Save figure")
    plt.tight_layout()
    outfile = os.path.join(OUTPUT_PATH, f"precip_accum.png")
    plt.savefig(outfile, dpi=400, bbox_inches='tight')
    plt.show()

    print(f"Figure saved: {outfile}")