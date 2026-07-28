import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from mod_prec import read_data, cut_area, activate_geo, load_sat, set_extent
from mod_prec import event_lat_max, event_lon_max, event_lat_min, event_lon_min

if __name__ == '__main__':
    # Variables
    time1, time2 = "2025-11-25", "2025-11-28"

    # Define paths
    station_path = r'./data/senyar_station.nc'
    sat_path = r'./data/sat/MSWEP/daily/daily.nc'
    era5_path = r'./data/era5/tp_daily_Senyar.nc'
    fac_path = r'./data/final_exp/factual/pr_SRF_daily.nc'
    mask_path = r'./data/shp/mask_aceh.nc'
    mask_val = 1

    # Read file
    ds_mask = cut_area(xr.open_dataset(mask_path))
    ds_stat = xr.open_dataset(station_path)
    ds_sat = load_sat(sat_path, time1, time2)
    ds_fac = xr.open_dataset(fac_path) # read_data(fac_path, ds_mask, time1, time2, mask_val)
    ds_era5 = xr.open_dataset(era5_path)

    # Slice time and take sum (station)
    pr_stat = ds_stat['RR'].sel(time=slice(time1, time2))
    pr_stat = pr_stat.sum(dim='time', skipna=False)
    df_stat = pr_stat.to_dataframe()
    df_stat = df_stat.dropna()
    print(df_stat)
    print(df_stat.index)

    # Slice time and take sum (satellite)
    pr_sat = ds_sat['precipitation'].sel(time=slice(time1, time2))
    pr_sat = pr_sat.sum(dim='time', skipna=False)

    # Slice time and take sum (factual)
    pr_fac = ds_fac['pr'].sel(time=slice(time1, time2))
    pr_fac = pr_fac.sum(dim='time', skipna=False) * 3600

    # Slice time and take sum (ERA5)
    pr_era5 = ds_era5['tp'].sel(valid_time=slice(time1, time2))
    pr_era5 = pr_era5.sum(dim='valid_time', skipna=False) * 1_000

    
    # Set up plot
    vmin, vmax = 0, 720
    fig = plt.figure(figsize=(12, 6))
    ax1 = fig.add_subplot(1, 3, 1, projection=ccrs.PlateCarree())
    ax2 = fig.add_subplot(1, 3, 2, projection=ccrs.PlateCarree())
    ax3 = fig.add_subplot(1, 3, 3, projection=ccrs.PlateCarree())
    axs = [ax1, ax2, ax3]

    # Set up colormap
    levels = np.arange(vmin, vmax, 10)
    base = plt.cm.terrain_r(np.linspace(0, 1, len(levels)-1))
    base[0] = [1, 1, 1, 1]
    cmap = mcolors.ListedColormap(base)
    norm = mcolors.BoundaryNorm(levels, ncolors=cmap.N + 1, extend='max')


    # Add factual precipitation map
    pcm = ax1.contourf(pr_fac.xlon, pr_fac.xlat, pr_fac.values.squeeze(), cmap=cmap, levels=levels, 
                        vmin=vmin, vmax=vmax, transform=ccrs.PlateCarree(), extend='max')
    ax1.set_title('Factual')

    # Add satellite data
    ax2.contourf(pr_sat.lon, pr_sat.lat, pr_sat.values, cmap=cmap, levels=levels,
                        vmin=vmin, vmax=vmax, transform=ccrs.PlateCarree(), extend='max')
    ax2.set_title('MSWEP')

    # Add ERA5 data
    ax3.contourf(pr_era5.longitude, pr_era5.latitude, 
                 pr_era5.values, cmap=cmap, levels=levels, 
                        vmin=vmin, vmax=vmax, transform=ccrs.PlateCarree(), extend='max')
    ax3.set_title('ERA5')

    # Decorate plot
    for ax in axs:
        activate_geo(ax, mask_ocean=False)
        set_extent(ax)
        # Add station plots
        ax.scatter(df_stat['longitude'], df_stat['latitude'], c=df_stat['RR'],
                    vmin=vmin, vmax=vmax, cmap=cmap, edgecolors='k')

    # Shared horizontal colorbar
    cbar = fig.colorbar(pcm, ax=axs, orientation="horizontal", pad=0.08, fraction=0.06, aspect=40)
    cbar.set_label('Accumulated precipitation 25-28Nov2025 (mm)')

    plt.show()