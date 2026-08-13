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
    lon_min, lon_max, lat_min, lat_max = 94, 106, -1.5, 7.5 # 90, 115, -5, 14
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    ax.set_xticks(np.arange(lon_min, lon_max, 4), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(lat_min, lat_max, 4), crs=ccrs.PlateCarree())
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(fontsize)
   
    ax.grid(c='gray', ls='--')
    ax.coastlines(linewidth=0.75)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)

def read_data(path, selected_time):
    # Open dataset
    ds_zg = xr.open_dataset(path).sel(time=selected_time)
    
    # Read coordinates for plotting
    lon, lat = ds_zg['lon'], ds_zg['lat']

    # Prepare variable
    zg = ds_zg['zg500']

    return lon, lat, zg

def plot_zg(ax, lon, lat, zg, zg_levels, title):
    setup(ax)
    cf = ax.contourf(lon, lat, zg, levels=zg_levels, cmap='jet', transform=ccrs.PlateCarree())
    ax.set_title(title, fontsize=fontsize, fontweight='bold')
    return cf

# General parameters
fontsize=8

if __name__ == '__main__':

    #%% Parameters    
    selected_time = "2025-11-25T09:00:00"

    # Output file
    path_out = './figs/dynamical'
    name_out = rf'zg500_all_model.png'

    # Input file
    path_in = './data/final_exp'

    # Set up figure
    fig = plt.figure(figsize=(9,8))
    axs = [
        fig.add_subplot(2, 2, 1, projection=ccrs.PlateCarree()),
        fig.add_subplot(2, 2, 2, projection=ccrs.PlateCarree()),
        fig.add_subplot(2, 2, 3, projection=ccrs.PlateCarree()),
        fig.add_subplot(2, 2, 4, projection=ccrs.PlateCarree()),
        ]

    # Plot parameter
    zg_levels  = np.linspace(5750, 5900, 20)   # hPa

    # Plot ERA5
    ds_era5 = xr.open_dataset('./data/era5/z500_daily.nc').sel(valid_time=selected_time).isel(pressure_level=0)
    zg_era5 = ds_era5['z'] / 9.8
    plot_zg(axs[0], zg_era5['longitude'], zg_era5['latitude'], zg_era5, zg_levels=zg_levels, title='ERA5')

    # Plot each scenario
    name_in_list = ['counterfactual/GWL-1.5', 'factual', 'counterfactual/GWL+1.5']
    file_name_list = ['zg500_ensmean_daily.nc', 'zg500_daily.nc', 'zg500_ensmean_daily.nc']
    title_list = ['past -1.5K', 'present', 'fut. +1.5K']

    for name_in, title, ax, file_name in zip(name_in_list, title_list, axs[1:], file_name_list):
        lon, lat, zg = read_data(os.path.join(path_in, name_in, file_name), selected_time)
        cf = plot_zg(ax, lon, lat, zg, zg_levels, title)

    cbar = fig.colorbar(cf, ax=axs, orientation='horizontal', pad=0.08, fraction=0.06)
    cbar.set_label("500 hPa Geopotential Height (m)", fontsize=fontsize, fontweight='bold')
    cbar.ax.tick_params(labelsize=fontsize)

    # Path out to save figure
    plt.savefig(os.path.join(path_out, name_out), dpi=400, bbox_inches='tight')
