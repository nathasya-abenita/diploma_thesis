from mod_pgw import *

def cfac_past_path(exp):
    return rf'./data/final_exp/counterfactual/GWL-1.5/{exp}/ivt_1000_700.nc'

def cfac_fut_path(exp):
    return rf'./data/final_exp/counterfactual/GWL+1.5/{exp}/ivt_1000_700.nc'

def plot_cfac(ax, path_func, stat):
    model_list_ori = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']
    tp_cfac_list = []
    for exp in model_list_ori:
        # Define path
        path_cfac = path_func(exp)
        # Read file
        ds_cfac = read_data(path_cfac, time1, time2, rename=True)
        # Accumulated rainfall
        tp_cfac = ds_cfac['ivt'].mean(dim='time')
        tp_cfac_list.append(tp_cfac)

    # Concatenate along a new dimension
    ens = xr.concat(tp_cfac_list, dim="ensemble")
    if stat == 'max':
        ens_stat = ens.max(dim="ensemble")
    elif stat == 'mean':
        ens_stat = ens.mean(dim='ensemble')
    else:
        raise ValueError ('check stat options again!')

    # Add precipitation color
    ax.pcolormesh(tp_cfac.xlon, tp_cfac.xlat, ens_stat, cmap=cmap, shading="auto",
            transform=ccrs.PlateCarree(), zorder=1, vmin=0, vmax=pr_max)
    
if __name__ == '__main__':
    # Parameters
    outfile = rf'./figs/compare/finals/map_ivt.png'
    stat = 'mean'

    time1, time2 = "2025-11-25", "2025-11-26"
    pr_max = 900
    pr_min = 0 # pr_max / 15 # divided by nlevel
    unit = r"Low-Level Integrated Vapor Transport 25-26Nov2025 (kg m s$^{-1}$)"

    # Colormap control
    nlevel = 15
    turbo = plt.cm.turbo(np.linspace(0, 1, nlevel-1))  # 7 colors from turbo
    transparent = np.array([[0, 0, 0, 0]])      # RGBA fully transparent
    colors = turbo # np.vstack([transparent, turbo])    # stack into 8-color colormap
    cmap = ListedColormap(colors)
    # cmap = 'turbo'

    # Prepare plot
    fig = plt.figure(figsize=(12, 5))
    axs =[fig.add_subplot(1, 3, 1, projection=ccrs.PlateCarree()),
        fig.add_subplot(1, 3, 2, projection=ccrs.PlateCarree()),
        fig.add_subplot(1, 3, 3, projection=ccrs.PlateCarree())]
    
    # Plot for factual
    path_fac = r'./data/final_exp/factual/ivt_1000_700.nc'
    ds_fac = read_data(path_fac, time1, time2, rename=True)
    tp_fac = ds_fac['ivt'].mean(dim="time")

    pcm = axs[1].pcolormesh(tp_fac.xlon, tp_fac.xlat, tp_fac, cmap=cmap, shading="auto",
                transform=ccrs.PlateCarree(), zorder=1, vmin=0, vmax=pr_max)
    
    # Plot for other scenarios
    plot_cfac(axs[0], path_func=cfac_past_path, stat=stat)
    plot_cfac(axs[2], path_func=cfac_fut_path, stat=stat)

    # Add title
    axs[1].set_title('present')
    axs[0].set_title('past -1.5K')
    axs[2].set_title('fut. +1.5K')

    # Activate boundaries and set extent
    for ax in axs:
        activate_geo(ax, mask_ocean=False)
        set_extent(ax)

    # Shared horizontal colorbar
    cbar = fig.colorbar(pcm, ax=axs, orientation="horizontal", pad=0.04, fraction=0.06, aspect=40)
    cbar.set_label(unit)
    plt.savefig(outfile, bbox_inches='tight')
