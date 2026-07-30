'''
Categories
- Data access
- Spatial analysis
- Statistics
- Plotting functions
'''

import os
import geopandas as gpd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.gridspec import GridSpec
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.stats import gaussian_kde

# Defined event box (Malacca Strait)
event_lon_min, event_lon_max = 94, 106 
event_lat_min, event_lat_max = -1.5, 7.5

# Defined event box (North Sumatra)
# event_lon_min, event_lon_max = 96, 104
# event_lat_min, event_lat_max = 0, 5

#%% Data access

def read_data(path, time1, time2, rename=False):
    ds = xr.open_dataset(path).sel(time=slice(time1, time2))
    if rename:
        ds = ds.rename({'lon': 'xlon', 'lat': 'xlat'})
    ds = cut_area(ds)
    return ds

def load_sat(nc_file, time1, time2):

    ds = xr.open_dataset(nc_file)
    ds = fix_longitude(ds)
    ds = ds.sel(time=slice(time1, time2))

    return ds

#%% Spatial processing

def fix_longitude(ds):

    if np.any(ds.lon > 180):
        ds['lon'] = (ds.lon + 180) % 360 - 180
        ds = ds.sortby('lon')

    return ds

def add_polygon(ax, polygon_path='./data/shp/Aceh.geojson'):
    gdf = gpd.read_file(polygon_path)
    gdf = gdf.to_crs(epsg=4326)
    gdf.boundary.plot(ax=ax, linestyle='-', color='tab:orange', zorder=10)

def mask_data(ds, ds_mask, mask_val=1):
    ds = ds.where(ds_mask.mask == mask_val, drop=True)
    return ds

def cut_area (ds):
    ds = ds.where(
                (ds.xlat >= min(event_lat_min, event_lon_max)) &
                (ds.xlat <= max(event_lat_min, event_lon_max)) &
                (ds.xlon >= event_lon_min) &
                (ds.xlon <= event_lon_max) ,
                drop=True
        )
    return ds

#%% Statistics functions

def compute_exceedance_prob(tp : np.array):
    values = tp.flatten()
    values = values[~np.isnan(values)]
    # values = values[values > pr_min]

    values = np.sort(values)
    cdf = np.arange(1, len(values)+1)/len(values)
    excd_prob = 1-cdf
    return excd_prob, values

def compute_ens_mean_std (val_list):
    stacked_val = np.stack(val_list)
    ens_val_mean = stacked_val.mean(axis=0)
    ens_val_std  = stacked_val.std(axis=0)
    return ens_val_mean, ens_val_std

#%% Plotting functions

def plot_density_simple(ax, tp : np.array, pr_min : float, pr_max : float, 
                        color=None, alpha=1, linewidth=None, label=None, linestyle=None):
    values = tp.flatten()
    values = values[~np.isnan(values)]
    # values = values[(values > pr_min) & (values < pr_max)]

    kde = gaussian_kde(values)

    x = np.linspace(pr_min, pr_max, 800)
    ax.plot(x, kde(x), color=color, alpha=alpha, label=label, linewidth=linewidth, linestyle=linestyle)

def plot_hist_simple(ax, tp : np.array, pr_min, pr_max, bins=25, color=None, alpha=1, label=None):
    values = tp.flatten()
    values = values[~np.isnan(values)]
    values = values[values > pr_min]

    ax.hist(values, bins=bins, range=(pr_min, pr_max),density=True,
        color=color,alpha=alpha, edgecolor="black", linewidth=0.5, label=label)

    ax.set_xlim(pr_min, None)

def plot_density(ax, tp_fac, tp_cfac, pr_max, pr_min, unit):
    values_fac = tp_fac.values.flatten()
    values_fac = values_fac[~np.isnan(values_fac)]
    values_fac = values_fac[values_fac > pr_min]

    values_cfac = tp_cfac.values.flatten()
    values_cfac = values_cfac[~np.isnan(values_cfac)]
    values_cfac = values_cfac[values_cfac > pr_min]

    kde_fac = gaussian_kde(values_fac)
    kde_cfac = gaussian_kde(values_cfac)

    x = np.linspace(
        min(values_fac.min(), values_cfac.min()),
        max(values_fac.max(), values_cfac.max()),
        500,
    )
    x = np.linspace(pr_min, pr_max, 500)
    
    ax.plot(x, kde_cfac(x), linewidth=4, color='k', label="Counterfactual")
    ax.plot(x, kde_fac(x), linewidth=4, color='tab:blue', label="Factual")
    
    ax.set_xlim(pr_min, pr_max)
    ax.set_xlabel(unit)
    ax.set_ylabel("Density")
    ax.legend()

    # Switch y-axis position
    ax.yaxis.set_ticks_position("right")
    ax.yaxis.set_label_position("right")

def set_extent(ax):
    ax.set_xlim(event_lon_min, event_lon_max)
    ax.set_ylim(event_lat_min, event_lat_max)

def plot_limit_change(ax, x1, x2, cc_line=True):
    ax.hlines(0, x1, x2, color='gray', linestyle='--')
    if cc_line:
        ax.hlines(7, x1, x2, label='CC. rate', color='tab:orange', linestyle='--')
        ax.hlines(14, x1, x2, label=r'2$\times$ CC. rate', color='tab:orange', linestyle=':')

def plot_hyetograph (ax, pr : xr.DataArray,
                     color=None, alpha=1, linewidth=None, label=None):
    pr_array = np.nanmean(pr.values, axis=(1, 2))
    ax.plot(pr.time, pr_array, color=color, alpha=alpha, linewidth=linewidth, label=label)

def plot_cum_hyetograph (ax, pr : xr.DataArray,
                     color=None, alpha=1, linewidth=None, label=None):
    pr_array = np.nanmean(pr.values, axis=(1, 2))
    ax.plot(pr.time, np.cumsum(pr_array), color=color, alpha=alpha, linewidth=linewidth, label=label)

def plot_exceedance_prob(ax, excd_prob, values, color=None, alpha=1, linewidth=None, label=None, linestyle=None):
    ax.semilogx(excd_prob, values, color=color, alpha=alpha, linewidth=linewidth, label=label, linestyle=linestyle)
    ax.set_xlim(1, 1e-6)   # reversed

def activate_geo (ax, mask_ocean=True):
    # Mask ocean with white
    if mask_ocean:
        ax.add_feature(cfeature.OCEAN, facecolor="white", zorder=2)

    # Land + coastlines
    ax.add_feature(cfeature.LAND, facecolor="none", edgecolor="none", zorder=3)
    ax.add_feature(cfeature.COASTLINE, linewidth=1, zorder=4)
    ax.add_feature(cfeature.BORDERS, linestyle=":", zorder=4)
