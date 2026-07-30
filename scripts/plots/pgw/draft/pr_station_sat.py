import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scripts.plots.pgw.draft.mod_prec import read_data, cut_area, activate_geo, load_sat, set_extent
from scripts.plots.pgw.draft.mod_prec import event_lat_max, event_lon_max, event_lat_min, event_lon_min

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
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # Set up colormap
    levels = np.arange(vmin, vmax, 10)
    base = plt.cm.terrain_r(np.linspace(0, 1, len(levels)-1))
    base[0] = [1, 1, 1, 1]
    cmap = mcolors.ListedColormap(base)
    norm = mcolors.BoundaryNorm(levels, ncolors=cmap.N + 1, extend='max')

    # Add satellite data
    cf = ax.contourf(pr_sat.lon, pr_sat.lat, pr_sat.values, cmap=cmap, levels=levels,
                        vmin=vmin, vmax=vmax, transform=ccrs.PlateCarree(), extend='max')
    ax.set_title('MSWEP')

    # Decorate plot
    activate_geo(ax, mask_ocean=False)
    set_extent(ax)

    # Add station plots
    ax.scatter(df_stat['longitude'], df_stat['latitude'], c=df_stat['RR'],
                vmin=vmin, vmax=vmax, cmap=cmap, edgecolors='k')

    # Add station codes
    
    # df_info = df_stat.copy().drop(columns=['station_name', 'latitude', 'longitude', 'RR'])
    # df_info['color'] = ['white' for _ in range (len(df_info))]
    # df_info['ha'] = ['left' for _ in range (len(df_info))]
    # df_info = df_info.drop(columns=['elevation'])
    # df_info.to_csv('./data/stat_info.csv')

    df_info = pd.read_csv('./data/stat_info.csv')
    df_info = df_info.set_index(keys='station')
    print(df_info.index)
    
    for code, row in df_stat.iterrows():
        ha = df_info.loc[int(code)]['ha']
        va = df_info.loc[int(code)]['va']
        color = df_info.loc[int(code)]['color']

        if va == np.nan:
            va = 'top'

        ax.text(row['longitude'], row['latitude'], int(code), fontsize=9, color=color, ha=ha, zorder=10,
                fontweight='bold', va=va)

    # Shared horizontal colorbar
    cbar = fig.colorbar(cf, ax=ax, orientation="horizontal", pad=0.08, fraction=0.06, aspect=40)
    cbar.set_label('Accumulated precipitation 25-28Nov2025 (mm)')

    plt.show()