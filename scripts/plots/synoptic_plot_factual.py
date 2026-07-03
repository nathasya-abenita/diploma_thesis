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

    selected_time_list = ["2025-11-25T12:00:00", "2025-11-26T11:30:00", "2025-11-27T11:30:00",
                          "2025-11-28T11:30:00", "2025-11-29T00:00:00"]
    # 2025-11-25T12:00:00  2025-11-26T11:30:00  2025-11-27T11:30:00  2025-11-28T11:30:00 2025-11-29T00:00:00

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

    for idx, selected_time in enumerate(selected_time_list):

        #%% Preparing data

        # Read files
        data_dir    = r'./data/best_3km/ibltyp_2_iocnzoq_2'
        ds_msl      = xr.open_dataset(os.path.join(data_dir, 'psl_SRF_daily.nc')).sel(time=selected_time).rename({"xlon": "lon", "xlat": "lat"})
        ds_tp       = xr.open_dataset(os.path.join(data_dir, 'pr_SRF_daily.nc')).sel(time=selected_time).rename({"xlon": "lon", "xlat": "lat"})
        ds_u10      = xr.open_dataset(os.path.join(data_dir, 'uas_SRF_daily.nc')).sel(time=selected_time).rename({"xlon": "lon", "xlat": "lat"})
        ds_v10      = xr.open_dataset(os.path.join(data_dir, 'vas_SRF_daily.nc')).sel(time=selected_time).rename({"xlon": "lon", "xlat": "lat"})

        # Read coordinates for plotting
        lon, lat = ds_msl['lon'], ds_msl['lat']

        # Prepare sea level pressure
        mslp = (ds_msl['psl'] / 100.0).squeeze() # [Pa] to [hPa]

        # Prepare precipitation
        tp = (ds_tp['pr'] * 3600).squeeze()

        # Near-surface wind speed
        u10 = ds_u10['uas'].squeeze()
        v10 = ds_v10['vas'].squeeze()

        #%% Plotings

        mslp_levels  = np.arange(990, 1020, 1)   # hPa
        prec_levels  = np.arange(0, 200, 20)     # mm/day

        # Plot
        ax = axs[idx]
        setup(ax)
        cf = ax.contourf(lon, lat, tp, levels=prec_levels, cmap='Blues', transform=ccrs.PlateCarree())
        ax.coastlines(linewidth=0.8, color='black', zorder=10) # ax.add_feature(cfeature.LAND, facecolor='lightgray', zorder=10)
        ct = ax.contour(lon, lat, mslp, levels=mslp_levels, linewidths=0.5, colors='black', transform=ccrs.PlateCarree())
        ax.set_title(f"{selected_time.split("T")[0]}", loc='left', fontsize=font_size, fontweight='bold')

        cbar = plt.colorbar(cf, ax=ax, pad=0.01, fraction=0.03)
        cbar.set_label("Precipitation (mm d⁻¹)", fontsize=font_size, fontweight='bold')
        cbar.ax.tick_params(labelsize=font_size)

        # Wind quiver
        # print(u10['lon'][::step].shape, u10['lat'][::step].shape, u10[::step, ::step].shape)
        qv = ax.quiver(u10['lon'][::step, ::step], u10['lat'][::step, ::step], u10[::step, ::step], v10[::step, ::step], scale=200, width=0.002, transform=ccrs.PlateCarree(), color='black')
        qk = ax.quiverkey(qv, 0.85, 1.05, 10, '10 m/s', labelpos="E", color='black')

    # Path out to save figure
    path_out = './figs/synoptic_factual'
    name_out = rf'synoptic.png'
    plt.tight_layout()
    plt.savefig(os.path.join(path_out, name_out), dpi=400, bbox_inches='tight')
