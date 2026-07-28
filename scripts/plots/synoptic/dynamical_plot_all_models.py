import os
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

def setup(ax):

    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    ax.set_xticks(np.arange(lon_min, lon_max, 4), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(lat_min, lat_max, 4), crs=ccrs.PlateCarree())
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(font_size)
   
    ax.grid(c='gray', ls='--')
    ax.coastlines(linewidth=0.75)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)


if __name__ == '__main__':

    #%% Parameters
    experiments = ['factual', 'counterfactual/GWL-1.5/tweak',
               'counterfactual/GWL-1.5/EC-Earth3-Veg', 
               'counterfactual/GWL-1.5/MPI-ESM1-2-HR',
               'counterfactual/GWL-1.5/NorESM2-MM']

    experiments_title = ['factual', 'counterfactual/tweak',
               'counterfactual/EC-Earth3-Veg', 
               'counterfactual/MPI-ESM1-2-HR',
               'counterfactual/NorESM2-MM']
    
    selected_time = "2025-11-25T12:00:00"

    # Domain
    lon_min, lon_max, lat_min, lat_max = 90, 115, -5, 14

    # Plot settings
    font_size = 8
    step = 40

    # Plot figure
    fig = plt.figure(figsize=(12, 6))
    axs = np.array([
        fig.add_subplot(2, 3, i+1, projection=ccrs.PlateCarree())
        for i in range(5)
    ])

    for idx, exp in enumerate(experiments):

        #%% Preparing data

        # Read files
        data_dir    = rf'./data/final_exp/{exp}'
        ds_zg      = xr.open_dataset(os.path.join(data_dir, 'zg850_pycordex.nc')).sel(time=selected_time)
        ds_hus       = xr.open_dataset(os.path.join(data_dir, 'hus850_pycordex.nc')).sel(time=selected_time)
        ds_ua      = xr.open_dataset(os.path.join(data_dir, 'ua850_pycordex.nc')).sel(time=selected_time)
        ds_va      = xr.open_dataset(os.path.join(data_dir, 'va850_pycordex.nc')).sel(time=selected_time)

        # Read coordinates for plotting
        lon, lat = ds_zg['lon'], ds_zg['lat']

        # Prepare sea level pressure
        zg = (ds_zg['zg850'] / 100.0) # [Pa] to [hPa]

        # Prepare specific humidty
        hus = ds_hus['hus850']

        # Near-surface wind speed
        ua = ds_ua['ua850']
        va = ds_va['va850']

        #%% Plotings

        zg_levels  = np.arange(990, 1020, 1)   # hPa
        hus_levels  = np.arange(0.000, 0.021, 0.0015)     #

        # Plot
        ax = axs[idx]
        setup(ax)
        cf = ax.contourf(lon, lat, hus, levels=hus_levels, cmap='Blues', transform=ccrs.PlateCarree())
        ax.coastlines(linewidth=0.8, color='black', zorder=10) # ax.add_feature(cfeature.LAND, facecolor='lightgray', zorder=10)
        ct = ax.contour(lon, lat, zg, levels=10, vmin=-12, vmax=15, linewidths=0.5, colors='white', transform=ccrs.PlateCarree())
        ax.set_title(f"{experiments_title[idx]}", loc='left', fontsize=font_size, fontweight='bold')

        cbar = plt.colorbar(cf, ax=ax, pad=0.01, fraction=0.03)
        cbar.set_label("Specific Humidty (g g⁻¹)", fontsize=font_size, fontweight='bold')
        cbar.ax.tick_params(labelsize=font_size)

        # Wind quiver
        qv = ax.quiver(ua['lon'][::step, ::step], va['lat'][::step, ::step], ua[::step, ::step], va[::step, ::step], scale=200, width=0.002, transform=ccrs.PlateCarree(), color='black')
        qk = ax.quiverkey(qv, 0.85, 1.05, 10, '10 m/s', labelpos="E", color='black')

    # Path out to save figure
    path_out = './figs/dynamical'
    name_out = rf'dynamical_evolution_all_model.png'
    plt.tight_layout()
    plt.savefig(os.path.join(path_out, name_out), dpi=400, bbox_inches='tight')
