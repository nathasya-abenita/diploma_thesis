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

    # selected_time_list = ("2025-11-24T12:00", "2025-11-25T12:00", "2025-11-28T12:00")
    start = "2025-11-24T06:00"
    end   = "2025-11-28T12:00"
    selected_time_list = pd.date_range(start=start, end=end, freq="6h")

    # Domain
    lon_min, lon_max, lat_min, lat_max = 90, 115, -5, 15

    # Plot settings
    font_size = 8
    step = 5

    for selected_time in selected_time_list:

        #%% Preparing data

        # Read files
        ds_msl = xr.open_dataset('./data/era5/msl_hr_Senyar.nc').sel(valid_time=selected_time)
        ds_qhum = xr.open_dataset('./data/era5/qhum_6hr_Senyar.nc').sel(valid_time=selected_time)
        ds_sst = xr.open_dataset('./data/era5/sst_hr_Senyar.nc').sel(valid_time=selected_time)
        ds_uwnd = xr.open_dataset('./data/era5/uwnd_6hr_Senyar.nc').sel(valid_time=selected_time)
        ds_vwnd = xr.open_dataset('./data/era5/vwnd_6hr_Senyar.nc').sel(valid_time=selected_time)
        ds_tp   = xr.open_dataset('./data/era5/tp_daily_Senyar.nc').sel(valid_time=selected_time.strftime("%Y-%m-%d"))

        # Read coordinates for plotting
        lon, lat = ds_msl['longitude'], ds_msl['latitude']

        # Prepare sea level pressure
        mslp = ds_msl['msl'] / 100.0 # [Pa] to [hPa]

        # Prepare sea surface temperature
        sst = ds_sst['sst']

        # Prepare specific humidity
        q = ds_qhum.sel(pressure_level=850)['q'] * 1_000 # [kg kg^{-1}] to [g kg^{-1}]

        # Prepare shear
        u10 = ds_uwnd.sel(pressure_level=10)['u']
        u200 = ds_uwnd.sel(pressure_level=200)['u']
        u850 = ds_uwnd.sel(pressure_level=850)['u']

        v10 = ds_vwnd.sel(pressure_level=10)['v']
        v200 = ds_vwnd.sel(pressure_level=200)['v']
        v850 = ds_vwnd.sel(pressure_level=850)['v']

        du = u200 - u850
        dv = v200 - v850
        shear = np.sqrt(du**2 + dv**2)
        wspd = np.sqrt(u10**2 + v10**2)

        # Prepare precipitation
        tp = ds_tp['tp'][0] * 1000 # [m/d] to [mm/d]

        #%% Plotings

        # Plot figure
        plt.figure(figsize=(10, 6))

        sst_levels   = np.arange(298, 306, 0.5)  # K
        mslp_levels  = np.arange(998, 1018, 1)   # hPa
        q_levels     = np.arange(0, 18, 1)       # g/kg
        shear_levels = np.arange(0, 26, 1)       # m/s
        prec_levels  = np.arange(0, 200, 20)     # mm/h

        # MSLP
        plt.subplot(2, 2, 1, projection=ccrs.PlateCarree())
        ax = plt.gca()
        setup(ax)
        cf = plt.contourf(lon, lat, sst, levels=sst_levels, cmap='bwr', transform=ccrs.PlateCarree())
        ax.add_feature(cfeature.LAND, facecolor='lightgray', zorder=10)
        ct = plt.contour(lon, lat, mslp, levels=np.arange(998, 1015, 0.5), linewidths=0.5, colors='black', transform=ccrs.PlateCarree())
        plt.title(f"(a) {selected_time}", loc='left', fontsize=font_size, fontweight='bold')
        cbar = plt.colorbar(cf, ax=ax, pad=0.01, fraction=0.03)
        cbar.set_label("SST (K)", fontsize=font_size, fontweight='bold')
        cbar.ax.tick_params(labelsize=font_size)

        # Wind shear
        plt.subplot(2, 2, 2, projection=ccrs.PlateCarree())
        ax = plt.gca()
        setup(ax)
        cf = plt.contourf(lon, lat, shear, levels=shear_levels, cmap='gist_ncar_r', transform=ccrs.PlateCarree())
        qv = plt.quiver(lon[::step], lat[::step], du[::step, ::step], dv[::step, ::step], scale=200, width=0.002, transform=ccrs.PlateCarree(), color='gray')
        plt.title("(b)", loc='left', fontsize=font_size, fontweight='bold')
        cbar = plt.colorbar(cf, ax=ax, pad=0.01, fraction=0.03)
        cbar.set_label("Wind shear (m s⁻¹)", fontsize=font_size, fontweight='bold')
        cbar.ax.tick_params(labelsize=font_size)

        # Specific humidity 
        plt.subplot(2, 2, 3, projection=ccrs.PlateCarree())
        ax = plt.gca()
        setup(ax)
        cf = plt.contourf(lon, lat, q, levels=q_levels, cmap='rainbow_r', transform=ccrs.PlateCarree())
        st = plt.streamplot(lon, lat, u10[:,:], v10[:,:], arrowsize=1, arrowstyle='->', color='white', density=1, linewidth=0.5)
        plt.title("(c)", loc='left', fontsize=font_size, fontweight='bold')
        cbar = plt.colorbar(cf, ax=ax, pad=0.01, fraction=0.03)
        cbar.set_label("Q (g kg⁻¹)", fontsize=font_size, fontweight='bold')
        cbar.ax.tick_params(labelsize=font_size)

        # Total precipitation 
        plt.subplot(2, 2, 4, projection=ccrs.PlateCarree())
        ax = plt.gca()
        setup(ax)
        cf = plt.contourf(lon, lat, tp, levels=prec_levels, cmap='Blues', transform=ccrs.PlateCarree())
        ct = plt.contour(lon, lat, tp, levels=prec_levels, linewidths=0.5, colors='gray', transform=ccrs.PlateCarree())
        plt.quiverkey(qv, 0.85, 1.05, 10, '10 m/s', labelpos="E")
        plt.title("(d)", loc='left', fontsize=font_size, fontweight='bold')
        cbar = plt.colorbar(cf, ax=ax, pad=0.01, fraction=0.03)
        cbar.set_label("Precipitation (mm d⁻¹)", fontsize=font_size, fontweight='bold')
        cbar.ax.tick_params(labelsize=font_size)

        # Path out to save figure
        path_out = './figs'
        name_out = rf'synoptic_{selected_time}.png'
        plt.savefig(os.path.join(path_out, name_out), dpi=400, bbox_inches='tight')
