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
font_size = 8
lon_min, lon_max, lat_min, lat_max = 90, 115, -5, 14

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
    # Define paths
    outfile = r'./figs/compare/tas.png'
    basefile = r'./data/final_exp/counterfactual/GWL-1.5'
    model_list = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']
    varfile = r'tas_SRF.nc'
    filenames = [os.path.join(basefile, model, varfile) for model in model_list]

    # Read file
    ds_list = [xr.open_dataset(file) for file in filenames]
    ds_fac = xr.open_dataset(os.path.join('./data/final_exp/factual/', varfile))

    # Set up plot
    fig = plt.figure(figsize=(12, 4))
    gs = GridSpec(1, 4, figure=fig)
    axs = [fig.add_subplot(gs[i], projection=ccrs.PlateCarree()) for i in range(4)]

    # Color and variable setting
    delta_level = np.arange(-3, 0.25, 0.5)  # K
    varname = 'tas'
    cmap = plt.get_cmap("viridis")
    norm = mcolors.BoundaryNorm(delta_level, cmap.N)
    # cmap = plt.get_cmap("RdBu_r")
    # norm = mcolors.TwoSlopeNorm(
    #     vmin=delta_level.min(),
    #     vcenter=0,
    #     vmax=delta_level.max()
    # )
    
    # Take factual simulation value
    var_fac = ds_fac[varname].squeeze().mean(dim='time')
    
    # Iterate over each data
    for i in range (len(ds_list)):
        ax = axs[i]
        ds = ds_list[i]
        model = model_list[i]

        # Plot variable
        cf = ax.contourf(ds['xlon'], ds['xlat'], ds[varname].squeeze().mean(dim='time') - var_fac, levels=delta_level, cmap=cmap, norm=norm,
                         extend='both', transform=ccrs.PlateCarree())
        # ax.add_feature(cfeature.LAND, facecolor='lightgray', zorder=10)
        ax.set_title(model, loc='left', fontsize=font_size, fontweight='bold')
        setup(ax)

    # Add colorbar only to the last axis
    cbar = plt.colorbar(cf, ax=axs, orientation='horizontal', pad=0.08, fraction=0.06, aspect=40)
    cbar.set_label(r"$\Delta \overline{T_{\text{2m}}}$ (K)", fontsize=font_size, fontweight='bold')
    cbar.ax.tick_params(labelsize=font_size)

    # View/save plot
    plt.savefig(outfile)