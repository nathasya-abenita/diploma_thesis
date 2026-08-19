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
import matplotlib.colors as mcolors
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

def read_data(path, time1, time2, rename=False, print_time=False, remove_spin_up=True): 
    ds = xr.open_dataset(path).sel(time=slice(time1, time2))

    if remove_spin_up:
        ds = ds.sel(time=~(
            (ds.time.dt.date == np.datetime64("2025-11-25")) &
            (ds.time.dt.hour >= 0) &
            (ds.time.dt.hour <= 0)
        ))

    if print_time:
        print(ds.time)
        
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
    gdf.boundary.plot(ax=ax, linestyle='-', color='tab:orange', zorder=5)

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

def compute_exceedance_prob(tp : np.array, bins='auto'):
    values = tp.flatten()
    values = values[~np.isnan(values)]
    # values = values[values > pr_min]

    values = np.sort(values)
    cdf = np.arange(1, len(values)+1)/len(values)
    excd_prob = 1-cdf

    density_prob, bin_edges = np.histogram(values, bins=bins, density=True)
    return excd_prob, values, density_prob, bin_edges

def compute_ens_mean_std (val_list):
    stacked_val = np.stack(val_list)
    ens_val_mean = stacked_val.mean(axis=0)
    ens_val_std  = stacked_val.std(axis=0)
    return ens_val_mean, ens_val_std

def compute_ens_med_std (val_list):
    stacked_val = np.stack(val_list)
    ens_val_mean = np.median(stacked_val, axis=0)
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

def plot_hist_simple(ax, da : np.array, val_min, val_max, bins=25, color=None, alpha=1, label=None):
    values = da.flatten()
    values = values[~np.isnan(values)]
    # values = values[values > val_min]

    ax.hist(values, bins=bins, range=(val_min, val_max),density=True,
        color=color,alpha=alpha, edgecolor="black", linewidth=0.5, label=label)

    ax.set_xlim(val_min, val_max)

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

def plot_exceedance_prob_simple(ax, excd_prob, values, color=None, alpha=1, linewidth=None, label=None, linestyle=None):
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

def plot_impact_markers(ax):

    # 1. Define specific coordinates from the sources
    # S1: Malalak, West Sumatra (Village destroyed by flood) [2]
    # S2: Bener Meriah, Aceh (Multiple shallow landslides) [2]
    sites = {
        'S1': (100.278, 0.3897), # 100°16'41"E, 0°23'23"N
        'S2': (97.204, 4.665),   # 97°12'15"E, 4°39'54"N
    }

    # A1-A4: Remote-Sensing Sites in Aceh (Bukit Barisan mountains) [4, 5]
    remote_sites = {
        'A1 (Burlah)': (96.67, 4.71),
        'A2 (Blangpanu)': (97.25, 4.68),
        'A3 (Uningmas)': (96.82, 4.86),
        'A4 (Perhutani)': (97.27, 4.61),
    }

    flood_hotspots = {
        'Idi Town (Aceh Timur)': (97.77, 4.95), # Approx coords
        'Lhokseumawe': (97.14, 5.18),
        'Sibolga': (98.78, 1.74),
        'Tarutung': (98.97, 2.01),
    }

    # 5. Plotting Disaster Points
    for name, (lon, lat) in sites.items():
        ax.plot(lon, lat, '^', color='k', markersize=2.5, zorder=10)
    # ax.plot([], [], 'o', color='k', label=f'Landslide Sites') # legend

    # Remote Sensing Sites A1-A4
    for name, (lon, lat) in remote_sites.items():
        ax.plot(lon, lat, '^', color='k', markersize=2.5, zorder=10)

    for name, (lon, lat) in flood_hotspots.items():
        ax.plot(lon, lat, '^', color='tab:red', markersize=2.5, zorder=10)
    # ax.plot([], [],'o', color='tab:red', label=f'Flood Sites') # legend

#%% Main class for PGW change analysis (spatial map and distribution graph)

class PGW:
    def __init__ (self, filename, val_min, val_max, unit, var_name, time_start, time_end, 
                  time_stat=None, ens_stat='mean', rename=False, val_modify_func=None, path_mask=None):
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

        if path_mask is not None:
            self.mask = True
            self.ds_mask = cut_area(xr.open_dataset(path_mask))
        else:
            self.mask = False

        self.model_list = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']

    def cfac_past_path(self, exp):
        return rf'./data/final_exp/counterfactual/GWL-1.5/{exp}/{self.filename}'

    def cfac_fut_path(self, exp):
        return rf'./data/final_exp/counterfactual/GWL+1.5/{exp}/{self.filename}'

    def compute_ens(self, scenario):
        tp_cfac_list = []
        for exp in self.model_list:
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
            ds[self.var_name] = self.val_modify_func(ds[self.var_name])

        if self.mask == True:
            ds = mask_data(ds, self.ds_mask)

        # Compute statistics in time
        if self.time_stat is not None:
            if self.time_stat == 'mean':
                val = ds[self.var_name].mean(dim='time')
            elif self.time_stat == 'max':
                val = ds[self.var_name].max(dim='time')
            elif self.time_stat == 'median':
                val = ds[self.var_name].median(dim='time')
            elif self.time_stat == 'sum':
                val = ds[self.var_name].sum(dim='time')
            else:
                raise ValueError ('check `time_stat` options!')
        else:
            val = ds[self.var_name]

        return val

    def plot_colormesh (self, ax, lon, lat, val, cmap, norm):
        pcm = ax.pcolormesh(lon, lat, val, cmap=cmap, norm=norm, shading="auto",
                            transform=ccrs.PlateCarree(), zorder=1,)
        return pcm
        
    def plot_map (self, outfile=None, polygon_path=None, cbar_n_level=20, add_impact_markers=False):

        # Colormap control
        colors = [
            (1.0, 1.0, 1.0, 1.0),   # white
            (0.6, 0.8, 1.0, 1.0),   # light blue (soft, pastel)
            (0.0, 0.7, 0.0, 1.0),   # green
            (1.0, 1.0, 0.0, 1.0),   # yellow
            (1.0, 0.0, 0.0, 1.0),   # red
        ]

        cmap = mcolors.LinearSegmentedColormap.from_list(
            "custom", colors, N=cbar_n_level
        )

        bounds = np.linspace(self.val_min, self.val_max, cbar_n_level)   # 10 intervals
        norm = mcolors.BoundaryNorm(boundaries=bounds, ncolors=cmap.N)

        # Prepare plot
        fig = plt.figure(figsize=(12, 5))
        axs =[fig.add_subplot(1, 3, 1, projection=ccrs.PlateCarree()),
            fig.add_subplot(1, 3, 2, projection=ccrs.PlateCarree()),
            fig.add_subplot(1, 3, 3, projection=ccrs.PlateCarree())]
        
        # Plot for factual
        path_fac = rf'./data/final_exp/factual/{self.filename}'
        tp_fac = self.prepare_data(path_fac)

        pcm = self.plot_colormesh(axs[1], tp_fac.xlon, tp_fac.xlat, tp_fac, cmap, norm)

        # Plot for other scenarios
        ens_val = self.compute_ens(scenario='past')
        self.plot_colormesh(axs[0], ens_val.xlon, ens_val.xlat, ens_val, cmap, norm)
        ens_val = self.compute_ens(scenario='fut.')
        self.plot_colormesh(axs[2], ens_val.xlon, ens_val.xlat, ens_val, cmap, norm)

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
            if add_impact_markers:
                plot_impact_markers(ax)

        # Shared horizontal colorbar
        cbar = fig.colorbar(pcm, ax=axs, orientation="horizontal", pad=0.04, extend='both', fraction=0.06, aspect=40)
        cbar.set_label(self.unit)
        cbar.set_ticks(bounds[::2])
        if outfile is not None:
            plt.savefig(outfile, bbox_inches='tight')
        return fig, axs

    def plot_exceedance_prob(self, ax, excd_prob, ens_mean, ens_std, linewidth=None, color=None, label=None):
        plot_exceedance_prob_simple(ax, excd_prob, ens_mean, linewidth=linewidth, color=color, label=label)
        ax.fill_between(excd_prob, ens_mean - ens_std, ens_mean + ens_std, 
                        color=color, alpha=0.2, edgecolor=None)

    def plot_pdf(self, ax, bin_edges, prob, linewidth=None, color=None, label=None, alpha=None):
        
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        ax.set_yscale('log')
        ax.scatter(bin_centers, prob, s=5, color=color, label=label, alpha=alpha, edgecolors=None)
        

    def plot_normal(self, ax, values, ens_mean, ens_std, linewidth=None, color=None, label=None):
        ax.plot(values, ens_mean, linewidth=linewidth, color=color, label=label)
        ax.fill_between(values, ens_mean - ens_std, ens_mean + ens_std, 
                        color=color, alpha=0.2, edgecolor=None)

    def compute_exceedance_prob_ens(self, values_fac, scenario, bins='auto'):
        values_cfac_list = []
        change_list = []
        dens_prob_list = []
        bin_edges_list = []
        
        # Plot members of counterfactual
        for exp in self.model_list:
            
            # Read data
            if scenario == 'past':
                path_cfac = self.cfac_past_path(exp)
            elif scenario == 'fut.':
                path_cfac = self.cfac_fut_path(exp)
            else:
                raise ValueError (r'check scenario input (choices: "past" or "fut.")')
            val_cfac = self.prepare_data(path_cfac)
            excd_prob, values, dens_prob, bin_edges = compute_exceedance_prob(val_cfac.values, bins=bins)
            values_cfac_list.append(values)

            if scenario == 'past':
                change = (values_fac - values) / values * 100
            elif scenario == 'fut.':
                change = (values - values_fac) / values_fac * 100
            else:
                raise ValueError (r'check scenario input (choices: "past" or "fut.")')
            change_list.append(change / 1.5) # convert unit to % per degree

            bin_edges_list.append(bin_edges)
            dens_prob_list.append(dens_prob)

        # Compute ensemble stats
        stacked_val = np.stack(values_cfac_list)      # shape: (n_ens, n_points)
        stacked_change = np.stack(change_list)

        if self.ens_stat == 'mean':
            ens_val_mean = stacked_val.mean(axis=0)        
            ens_change_mean = stacked_change.mean(axis=0)
        elif self.ens_stat == 'median':
            ens_val_mean = np.median(stacked_val, axis=0)
            ens_change_mean = np.median(stacked_change, axis=0)
        elif self.ens_stat == 'max':
            ens_val_mean = stacked_val.max(axis=0)        
            ens_change_mean = stacked_change.max(axis=0)

        # Compute spread
        ens_val_std  = stacked_val.std(axis=0)
        ens_change_std = stacked_change.std(axis=0)
        return excd_prob, ens_val_mean, ens_val_std, ens_change_mean, ens_change_std, dens_prob_list, bin_edges_list

    def plot_dist_change(self, change_val_min, change_val_max, change_min=0, change_max=20, outfile=None, add_cc_limit=False, pct=0.99, bins='auto', ylim_pdf=(1e-6, 1)):
        # Set up plot
        lw = 3
        alpha_cf = 0.2
        fig, axs = plt.subplots(1, 3, figsize=(12, 4))

        # Compute factual
        path_fac = rf'./data/final_exp/factual/{self.filename}'
        val_fac = self.prepare_data(path_fac)
        excd_prob, values_fac, dens_prob_fac, bin_edges_fac = compute_exceedance_prob(val_fac.values, bins=bins)

        # Plot counterfactuals (past/1)
        print('plotting counterfactuals of past dist')
        excd_prob, ens_val_mean1, ens_val_std1, ens_change_mean1, ens_change_std1, dens_prob_list1, bin_edges_list1 = self.compute_exceedance_prob_ens(values_fac, scenario='past', bins=bins)
        self.plot_exceedance_prob(axs[0], excd_prob, ens_val_mean1, ens_val_std1,
                                  linewidth=lw, color='tab:blue', label='past -1.5K')
        self.plot_normal(axs[1], ens_val_mean1, ens_change_mean1, ens_change_std1,
                                      linewidth=lw, color='tab:blue', label='past to present')
        # plot_density_simple(axs[2], ens_val_mean, pr_min=pr_min, pr_max=pr_max, color='tab:blue', linewidth=lw/2, label='past -1.5K')
        #plot_hist_simple(axs[2], ens_val_mean1, val_min=self.val_min, val_max=self.val_max, color='tab:blue', alpha=0.25, label='past -1.5K')
        for i in range (len(self.model_list)):
            dens_prob, bin_edges = dens_prob_list1[i], bin_edges_list1[i]
            if i == 0:
                self.plot_pdf(axs[2], bin_edges, dens_prob, color='tab:blue', label='past -1.5K', alpha=alpha_cf)
            else:
                self.plot_pdf(axs[2], bin_edges, dens_prob, color='tab:blue', alpha=alpha_cf)

        # Plot factual
        print('plotting factual dist')
        plot_exceedance_prob_simple(axs[0], excd_prob, values_fac, linewidth=lw, color='k', label='present')
        # plot_density_simple(axs[2], values_fac, pr_min=pr_min, pr_max=pr_max, color='k', linestyle='--', linewidth=lw/2, label='present')
        #plot_hist_simple(axs[2], values_fac, val_min=self.val_min, val_max=self.val_max, color='k', alpha=0.25, label='present')
        self.plot_pdf(axs[2], bin_edges_fac, dens_prob_fac, color='k', label='present', alpha=1)

        # Plot counterfactuals (future/2)
        print('plotting counterfactuals of future dist')
        excd_prob, ens_val_mean2, ens_val_std2, ens_change_mean2, ens_change_std2, dens_prob_list2, bin_edges_list2 = self.compute_exceedance_prob_ens(values_fac, scenario='fut.', bins=bins)
        self.plot_exceedance_prob(axs[0], excd_prob, ens_val_mean2, ens_val_std2,
                                    linewidth=lw, color='tab:red', label='fut. +1.5K')
        self.plot_normal(axs[1], values_fac, ens_change_mean2, ens_change_std2,
                                        linewidth=lw, color='tab:red', label='present to fut.')
        # plot_density_simple(axs[2], ens_val_mean, pr_min=pr_min, pr_max=pr_max, color='tab:red', linestyle=':', linewidth=lw/2, label='fut. +1.5K')
        # plot_hist_simple(axs[2], ens_val_mean2, val_min=self.val_min, val_max=self.val_max, color='tab:red', alpha=0.25, label='fut. +1.5K')
        for i in range (len(self.model_list)):
            dens_prob, bin_edges = dens_prob_list2[i], bin_edges_list2[i]
            if i == 0:
                self.plot_pdf(axs[2], bin_edges, dens_prob, color='tab:red', label='fut. +1.5K', alpha=alpha_cf)
            else:
                self.plot_pdf(axs[2], bin_edges, dens_prob, color='tab:red', alpha=alpha_cf)
        
        # Change per degree warming plot
        # # combined mean
        # ens_change_mean = (ens_change_mean1 + ens_change_mean2) / 2
        # # combined variance
        # ens_change_var = (
        #     (ens_change_std1**2 + ens_change_mean1**2) + (ens_change_std2**2 + ens_change_mean2**2)
        # ) / 2 - ens_change_mean**2
        # ens_change_std = ens_change_var ** 0.5
        # plot_cfac_normal_plot(axs[1], ens_val_mean, ens_change_mean, ens_change_std, linewidth=lw, color='k', label='all')
    
        # Setting axis
        axs[1].set_xlim(change_val_min, change_val_max)
        axs[1].set_ylim(change_min, change_max)
        if add_cc_limit:
            plot_limit_change(axs[1], x1=change_val_min, x2=change_val_max)
    
        # Decorate plots
        axs[0].set_ylabel(self.unit)
        axs[0].set_xlabel('Exceedance Probability')
        axs[0].legend(loc='upper left')

        if add_cc_limit:
            axs[1].legend(ncols=2, loc='upper center')
        else:
            axs[1].legend(ncols=1, loc='upper center')
        axs[1].set_ylabel('Change per degree global\nwarming (% K$^{-1}$)')
        axs[1].set_xlabel(self.unit)
    
        axs[2].legend(loc='upper right')
        axs[2].set_ylim(ylim_pdf)
        axs[2].set_ylabel('Density')
        axs[2].set_xlabel(self.unit)

        plt.tight_layout()
        if outfile is not None:
            plt.savefig(outfile + '.png', bbox_inches='tight')
    
        # Extract percentile
        idx = np.searchsorted(excd_prob[::-1], 1-pct)
        pct_present = values_fac[-idx-1]
        pct_past = ens_val_mean1[-idx-1]
        pct_fut = ens_val_mean2[-idx-1]
        pct_past_present_change = ens_change_mean1[-idx-1]
        pct_present_fut_change = ens_change_mean2[-idx-1]

        # Extract median change
        med_past_present_change = np.nanmedian(ens_change_mean1)
        med_present_fut_change = np.nanmedian(ens_change_mean2)

        with open(f"{outfile}.txt", "w") as f:
            f.write(f"pct: {pct}\n")
            f.write(f"pct: {pct_past: .3f}, {pct_present: .3f}, {pct_fut: .3f}\n")
            f.write(f"pct_change: {pct_past_present_change * 1.5: .1f}, {pct_present_fut_change * 1.5: .1f}\n")
            f.write(f"med_change: {med_past_present_change * 1.5: .1f}, {med_present_fut_change * 1.5: .1f}\n")
        return fig, axs