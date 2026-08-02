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
    spin_up_time = [f"2025-11-25T{h:02d}:00:00" for h in range(1, 12)]
    
    ds = xr.open_dataset(path).sel(time=slice(time1, time2))
    ds = ds.sel(time=~ds.time.isin(spin_up_time)) # delete spin up time

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

def plot_polygon(ax, polygon_path='./data/shp/Aceh.geojson'):
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

#%% Map Class: Spatial change

class SpatialMap:
    def __init__ (self, filename, val_min, val_max, unit, var_name, time_start, time_end, 
                  cmap=None, time_stat='mean', ens_stat='mean', rename=False, val_modify_func=None):
        self.filename = filename
        self.time_start = time_start
        self.time_end = time_end
        self.time_stat = time_stat
        self.ens_stat = ens_stat

        self.rename = rename # if True, rename lon to xlon; lat to xlat

        # Values
        self.val_min, self.val_max = val_min, val_max
        self.unit = unit
        self.var_name = var_name
        self.val_modify_func = val_modify_func
    
        # Colormap control
        if cmap is None:
            nlevel = 10
            turbo = plt.cm.turbo(np.linspace(0, 1, nlevel-1))  # 7 colors from turbo
            transparent = np.array([[0, 0, 0, 0]])      # RGBA fully transparent
            colors = np.vstack([transparent, turbo])    # stack into 8-color colormap
            self.cmap = ListedColormap(colors)
        else:
            self.cmap = cmap

    def cfac_past_path(self, exp):
        return rf'./data/final_exp/counterfactual/GWL-1.5/{exp}/{self.filename}'

    def cfac_fut_path(self, exp):
        return rf'./data/final_exp/counterfactual/GWL+1.5/{exp}/{self.filename}'

    def prepare_cfac(self, scenario):
        model_list_ori = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']
        tp_cfac_list = []
        for exp in model_list_ori:
            # Define path
            if scenario == 'past':
                path_cfac = self.cfac_past_path(exp)
            elif scenario == 'fut.':
                path_cfac = self.cfac_fut_path(exp)
            else:
                raise ValueError (r'check scenario input (choices: "past" or "fut.")')
            # Read file
            tp_cfac = self.prepare_data(path_cfac)
            tp_cfac_list.append(tp_cfac)

        # Concatenate along a new dimension
        ds_ens = xr.concat(tp_cfac_list, dim="ensemble")
        if self.ens_stat == 'max':
            ens_val = ds_ens.max(dim="ensemble")
        elif self.ens_stat == 'mean':
            ens_val = ds_ens.mean(dim='ensemble')
        elif self.ens_stat == 'median':
            ens_val = ds_ens.median(dim='ensemble')
        else:
            raise ValueError ('check stat options again!')
        return ens_val

    def prepare_data (self, path) -> xr.DataArray:
        # Read data and modify if wanted
        ds = read_data(path, self.time_start, self.time_end, rename=self.rename)
        if self.val_modify_func is not None:
            ds[self.var_name] = self.val_modify_func(ds[self.val_name])

        # Compute statistics in time
        if self.time_stat == 'mean':
            val = ds[self.var_name].mean(dim='time')
        elif self.time_stat == 'max':
            val = ds[self.var_name].max(dim='time')
        elif self.time_stat == 'median':
            val = ds[self.var_name].median(dim='time')
        else:
            raise ValueError ('check `time_stat` options!')
        return val

    def plot_colormesh (self, ax, lon, lat, val):
        pcm = ax.pcolormesh(lon, lat, val, cmap=self.cmap, shading="auto",
                            transform=ccrs.PlateCarree(), zorder=1, vmin=self.val_min, vmax=self.val_max)
        return pcm
        
    def plot_map (self, outfile, polygon_path=None):
    
        # Prepare plot
        fig = plt.figure(figsize=(12, 5))
        axs =[fig.add_subplot(1, 3, 1, projection=ccrs.PlateCarree()),
            fig.add_subplot(1, 3, 2, projection=ccrs.PlateCarree()),
            fig.add_subplot(1, 3, 3, projection=ccrs.PlateCarree())]
        
        # Plot for factual
        path_fac = rf'./data/final_exp/factual/{self.filename}'
        tp_fac = self.prepare_data(path_fac)

        pcm = self.plot_colormesh(axs[0], tp_fac.xlon, tp_fac.xlat, tp_fac)

        # Plot for other scenarios
        ens_val = self.prepare_cfac(scenario='past')
        self.plot_colormesh(axs[1], ens_val.xlon, ens_val.xlat, ens_val)
        ens_val = self.prepare_cfac(scenario='fut.')
        self.plot_colormesh(axs[2], ens_val.xlon, ens_val.xlat, ens_val)

        # Add title
        axs[1].set_title('present')
        axs[0].set_title('past -1.5K')
        axs[2].set_title('fut. +1.5K')

        # Activate boundaries and set extent
        for ax in axs:
            activate_geo(ax, mask_ocean=False)
            set_extent(ax)
            if polygon_path is not None:
                plot_polygon(ax, polygon_path=polygon_path)

        # Shared horizontal colorbar
        cbar = fig.colorbar(pcm, ax=axs, orientation="horizontal", pad=0.04, extend='both', fraction=0.06, aspect=40)
        cbar.set_label(self.unit)
        return plt.savefig(outfile, bbox_inches='tight')

#%% Distribution Class