import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scripts.plots.pgw.draft.mod_prec import read_data, cut_area, load_sat
from scripts.plots.pgw.draft.mod_prec import event_lat_max, event_lon_max, event_lat_min, event_lon_min
import matplotlib.dates as mdates

def extract_pr_model(pr : xr.DataArray, lon, lat):
    dist2 = (pr.xlat - lat)**2 + (pr.xlon - lon)**2

    iy, ix = np.unravel_index(dist2.argmin().item(), dist2.shape)

    point = pr.isel(iy=iy, jx=ix)
    print(float(lon), float(lat))
    print(point.coords)
    return point

def extract_pr_sat(pr : xr.DataArray, lon, lat):
    pr = pr.sel(lon=lon, lat=lat, method='nearest')
    return pr


    

if __name__ == '__main__':

    stat_code_list = ['96015', '96041', '96167', '96037', '96163', '96073', '96011', '96009',
    '96071', '96017', '96033', '96001', '96031', '96161', '96043', '96035']

    stat_code_list = np.sort([int(code) for code in stat_code_list]).astype('str')

    # Variables
    time1, time2 = "2025-11-25", "2025-11-28"
    dates = pd.date_range(time1, time2, freq="D")

    # Define paths
    station_path = r'./data/senyar_station.nc'
    sat_path = r'./data/sat/MSWEP/daily/daily.nc'
    fac_path = r'./data/final_exp/factual/pr_SRF_daily.nc'

    # Read file and slice time
    ds_stat = xr.open_dataset(station_path).sel(time=slice(time1, time2))
    ds_sat = load_sat(sat_path, time1, time2)
    ds_fac = cut_area(xr.open_dataset(fac_path).sel(time=slice(time1, time2)))

    # Prepare DataArray
    pr_stat = ds_stat['RR']
    pr_sat = ds_sat['precipitation']
    pr_fac = ds_fac['pr'] * 3600

    # Prepare plot for daily evolution
    fig, axes = plt.subplots(4, 4, figsize=(14,9), sharex=True)
    axes = axes.flatten()

    # Iterate over each code
    for ax, code in zip(axes, stat_code_list):
        # Prepare daily data
        ts_stat = pr_stat.sel(station=code)
        lon, lat = ts_stat.longitude, ts_stat.latitude
        ts_sat = extract_pr_sat(pr_sat, lon, lat)
        ts_fac = extract_pr_model(pr_fac, lon, lat)

        # Check accumulated values
        acc_stat = ts_stat.values.sum()
        acc_sat = ts_sat.values.sum()
        acc_fac = ts_fac.values.sum()

        # Plot daily evolution
        ax.plot(dates, ts_stat.values, label=f'station : {acc_stat:.0f} mm')
        ax.plot(dates, ts_sat.values, label=f'MSWEP : {acc_sat:.0f} mm')
        ax.plot(dates, ts_fac.values, label=f'Factual : {acc_fac:.0f} mm')
        ax.set_title(code)
        # Decorators
        # ax.set_xlabel('Date')
        ax.legend()
        ax.set_ylabel('Precipitation (mm)')


        # daily ticks
        ax.xaxis.set_major_locator(mdates.DayLocator())

        # show only day number (25, 26, 27...)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))

        # rotate if needed
        ax.tick_params(axis='x', rotation=0)
    
    # Activate legend
    ax.set_xlabel('Date')

    # handles, labels = axes[0].get_legend_handles_labels()
    # fig.legend(handles, labels, loc="lower center", ncol=len(labels))

    # Add title
    fig.suptitle("November 2025 Daily Precipitation", fontsize=12)

    fig.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig('./figs/daily_pr_with_station.png')


