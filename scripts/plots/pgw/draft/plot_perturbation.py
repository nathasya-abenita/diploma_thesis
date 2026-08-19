import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

# Plot settings
font_size = 14
lon_min, lon_max, lat_min, lat_max = 90, 115, -5, 14

def setup(ax):

    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    ax.set_xticks([]) 
    ax.set_yticks([]) 
    # ax.set_xticks(np.arange(lon_min, lon_max, 3), crs=ccrs.PlateCarree())
    # ax.set_yticks(np.arange(lat_min, lat_max, 3), crs=ccrs.PlateCarree())
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(font_size)
   
    ax.grid(c='gray', ls='--')
    ax.coastlines(linewidth=0.75)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)

if __name__ == '__main__':
    # Define paths
    outfile = r'./figs/compare/ts_complete.png'
    basefile = lambda x : rf'./data/final_exp/counterfactual/GWL{x}1.5'
    model_list = ['past -1.5K (tweak)', 'past -1.5K (EC-Earth3-Veg)', 'past -1.5K (MPI-ESM1-2-HR)', 'past -1.5K (NorESM2-MM)',
                  'fut. +1.5K (tweak)', 'fut. +1.5K (EC-Earth3-Veg)', 'fut. +1.5K (MPI-ESM1-2-HR)', 'fut. +1.5K (NorESM2-MM)'] # for title
    model_list_ori = ['EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']
    varfile = r'delta_ts.nc'
    filenames = [os.path.join(basefile('-'), model, varfile) for model in model_list_ori]
    filenames += [os.path.join(basefile('+'), model, varfile) for model in model_list_ori]

    # Read file
    ds_list_temp = [xr.open_dataset(file) for file in filenames]

    ds_past = ds_list_temp[-1].copy()
    ds_past["ts"] = xr.full_like(ds_past["ts"], -1.5)
    ds_fut = ds_list_temp[-1].copy()
    ds_fut["ts"] = xr.full_like(ds_fut["ts"], 1.5)
    ds_list = [ds_past] + ds_list_temp[:3] + [ds_fut] + ds_list_temp[3:]

    # print(ds_fut['ts'])
    
    # Set up plot
    fig = plt.figure(figsize=(18,9))
    axs = [fig.add_subplot(2, 4, i, projection=ccrs.PlateCarree()) for i in range (1, 8+1)]

    # Color and variable setting
    delta_level = np.arange(-3, 3.5, 0.5)  # K
    varname = 'ts'
    cmap = plt.get_cmap("RdBu_r")
    norm = mcolors.BoundaryNorm(delta_level, cmap.N)

    # Iterate over each data
    for i in range (len(ds_list)):
        print(i)
        ax = axs[i]
        ds = ds_list[i]
        model = model_list[i]

        # Plot variable
        cf = ax.contourf(ds['xlon'], ds['xlat'], ds[varname].mean(dim='time'), levels=delta_level, cmap=cmap, norm=norm,
                        extend='both', transform=ccrs.PlateCarree())
        # ax.add_feature(cfeature.LAND, facecolor='lightgray', zorder=10)
        ax.set_title(model, loc='left', fontsize=font_size, fontweight='bold')
        setup(ax)

    # Add colorbar only to the last axis
    cbar = plt.colorbar(cf, ax=axs, orientation='horizontal', pad=0.08, fraction=0.06, aspect=40, ticks=delta_level)
    cbar.set_label(r"$\overline{\Delta T_{\text{sfc}}}$ (K)", fontsize=font_size, fontweight='bold')
    cbar.ax.tick_params(labelsize=font_size)

    # View/save plot
    plt.savefig(outfile, bbox_inches='tight')