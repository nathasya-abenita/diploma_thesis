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

    selected_time_list = ["2025-11-24", "2025-11-25", "2025-11-28"]
    # start = "2025-11-24T06:00"
    # end   = "2025-11-28T12:00"
    # selected_time_list = pd.date_range(start=start, end=end, freq="6h")

    # Domain
    lon_min, lon_max, lat_min, lat_max = 90, 115, -5, 15

    # Plot settings
    font_size = 8
    step = 5

    # Plot figure
    fig = plt.figure(figsize=(12, 12))
    axs = np.array([
        fig.add_subplot(4, 3, i+1, projection=ccrs.PlateCarree())
        for i in range(12)
    ]).reshape(4, 3)

    for idx, selected_time in enumerate(selected_time_list):

        #%% Preparing data

        # Read files
        ds_msl = xr.open_dataset('./data/era5/msl_daily_Senyar.nc').sel(valid_time=selected_time)
        ds_qhum = xr.open_dataset('./data/era5/qhum_daily_Senyar.nc').sel(valid_time=selected_time)
        ds_sst = xr.open_dataset('./data/era5/sst_daily_Senyar.nc').sel(valid_time=selected_time)
        ds_uwnd = xr.open_dataset('./data/era5/uwnd_daily_Senyar.nc').sel(valid_time=selected_time)
        ds_vwnd = xr.open_dataset('./data/era5/vwnd_daily_Senyar.nc').sel(valid_time=selected_time)
        ds_tp   = xr.open_dataset('./data/era5/tp_daily_Senyar.nc').sel(valid_time=selected_time)
        ds_u10 = xr.open_dataset('./data/era5/u10_v10_daily_Senyar.nc').sel(valid_time=selected_time)
        ds_v10 = ds_u10.copy()

        # Read coordinates for plotting
        lon, lat = ds_msl['longitude'], ds_msl['latitude']

        # Prepare sea level pressure
        mslp = (ds_msl['msl'] / 100.0).squeeze() # [Pa] to [hPa]

        # Prepare sea surface temperature
        sst = ds_sst['sst'].squeeze()
        # Prepare specific humidity
        q = (ds_qhum.sel(pressure_level=850)['q'] * 1_000 ).squeeze() # [kg kg^{-1}] to [g kg^{-1}]

        # Prepare shear
        u10 = ds_u10['u10'].squeeze()
        u200 = ds_uwnd.sel(pressure_level=200)['u'].squeeze()
        u850 = ds_uwnd.sel(pressure_level=850)['u'].squeeze()

        v10 = ds_v10['v10'].squeeze()
        v200 = ds_vwnd.sel(pressure_level=200)['v'].squeeze()
        v850 = ds_vwnd.sel(pressure_level=850)['v'].squeeze()

        du = u200 - u850
        dv = v200 - v850
        shear = np.sqrt(du**2 + dv**2)
        wspd = np.sqrt(u10**2 + v10**2)

        # Prepare precipitation
        tp = (ds_tp['tp'][0] * 1000).squeeze() # [m/d] to [mm/d]

        #%% Plotings

        sst_levels   = np.arange(298, 306, 0.5)  # K
        mslp_levels  = np.arange(990, 1020, 1)   # hPa
        q_levels     = np.arange(0, 18, 1)       # g/kg
        shear_levels = np.arange(0, 30, 1)       # m/s
        prec_levels  = np.arange(0, 200, 20)     # mm/h

        # MSLP
        # plt.subplot(3, 4, idx, projection=ccrs.PlateCarree())
        ax = axs[0, idx] #plt.gca()
        setup(ax)
        cf = ax.contourf(lon, lat, sst, levels=sst_levels, cmap='bwr', transform=ccrs.PlateCarree())
        ax.add_feature(cfeature.LAND, facecolor='lightgray', zorder=10)
        ct = ax.contour(lon, lat, mslp, levels=np.arange(998, 1015, 0.5), linewidths=0.5, colors='black', transform=ccrs.PlateCarree())
        ax.set_title(f"({idx*4 + 1}) {selected_time}", loc='left', fontsize=font_size, fontweight='bold')
        cbar = plt.colorbar(cf, ax=ax, pad=0.01, fraction=0.03)
        cbar.set_label("SST (K)", fontsize=font_size, fontweight='bold')
        cbar.ax.tick_params(labelsize=font_size)

        # Wind shear
        # plt.subplot(3, 4, idx+1, projection=ccrs.PlateCarree())
        ax = axs[1, idx] #plt.gca()
        setup(ax)
        cf = ax.contourf(lon, lat, shear, levels=shear_levels, cmap='gist_ncar_r', transform=ccrs.PlateCarree())
        qv = ax.quiver(lon[::step], lat[::step], du[::step, ::step], dv[::step, ::step], scale=200, width=0.002, transform=ccrs.PlateCarree(), color='gray')
        ax.quiverkey(qv, 0.85, 1.05, 10, '10 m/s', labelpos="E")
        ax.set_title(f"({idx*4 + 2})", loc='left', fontsize=font_size, fontweight='bold')
        cbar = plt.colorbar(cf, ax=ax, pad=0.01, fraction=0.03)
        cbar.set_label("Wind shear (m s⁻¹)", fontsize=font_size, fontweight='bold')
        cbar.ax.tick_params(labelsize=font_size)

        # Specific humidity 
        # plt.subplot(3, 4, idx+2, projection=ccrs.PlateCarree())
        ax = axs[2, idx] #plt.gca()
        setup(ax)
        cf = ax.contourf(lon, lat, q, levels=q_levels, cmap='rainbow_r', transform=ccrs.PlateCarree())
        # st = ax.streamplot(u10['longitude'], u10['latitude'], u10[:,:], v10[:,:], arrowsize=1, arrowstyle='->', color='white', density=1, linewidth=0.5)
        
        qv = ax.quiver(u10['longitude'][::step], u10['latitude'][::step], u10[::step, ::step], v10[::step, ::step], scale=200, width=0.002, transform=ccrs.PlateCarree(), color='white')
        qk = ax.quiverkey(qv, 0.85, 1.05, 10, '10 m/s', labelpos="E", color='black')

        # Add background to the label
        ax.set_title(f"({4*idx + 3})", loc='left', fontsize=font_size, fontweight='bold')
        cbar = plt.colorbar(cf, ax=ax, pad=0.01, fraction=0.03)
        cbar.set_label("Q (g kg⁻¹)", fontsize=font_size, fontweight='bold')
        cbar.ax.tick_params(labelsize=font_size)

        # Total precipitation 
        # plt.subplot(3, 4, idx+3, projection=ccrs.PlateCarree())
        ax = axs[3, idx] #plt.gca()
        setup(ax)
        cf = ax.contourf(lon, lat, tp, levels=prec_levels, cmap='Blues', transform=ccrs.PlateCarree())
        ct = ax.contour(lon, lat, tp, levels=prec_levels, linewidths=0.5, colors='gray', transform=ccrs.PlateCarree())
        ax.set_title(f"({4*idx + 4})", loc='left', fontsize=font_size, fontweight='bold')
        cbar = plt.colorbar(cf, ax=ax, pad=0.01, fraction=0.03)
        cbar.set_label("Precipitation (mm d⁻¹)", fontsize=font_size, fontweight='bold')
        cbar.ax.tick_params(labelsize=font_size)

    # Path out to save figure
    path_out = './figs'
    name_out = rf'synoptic.png'
    plt.tight_layout()
    plt.savefig(os.path.join(path_out, name_out), dpi=400, bbox_inches='tight')
