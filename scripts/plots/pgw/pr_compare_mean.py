from mod_prec import *

def cfac_path(exp):
    return rf'./data/final_exp/counterfactual/GWL-1.5/{exp}/pr_SRF.nc'

if __name__ == '__main__':
    # Parameters
    outfile = rf'./figs/compare/pr_mean_map.png'
    time1, time2 = "2025-11-25", "2025-11-26"
    pr_max = 15
    pr_min = 0 # pr_max / 15 # divided by nlevel
    unit = r"Average Intensity (mm h$^{-1}$)"

    # Colormap control
    nlevel = 15
    turbo = plt.cm.turbo(np.linspace(0, 1, nlevel-1))  # 7 colors from turbo
    transparent = np.array([[0, 0, 0, 0]])      # RGBA fully transparent
    colors = np.vstack([transparent, turbo])    # stack into 8-color colormap
    cmap = ListedColormap(colors)

    # Define paths
    exp = 'ensemble'
    path_fac = r'./data/final_exp/factual/pr_SRF.nc'
    path_cfac = cfac_path(exp)
    path_mask = r'./data/shp/mask_aceh.nc' #r'./data/counterfactual/mask_SRF.nc'
    mask_val = 1 # 2

    # Read file
    ds_mask = cut_area(xr.open_dataset(path_mask))
    ds_fac = read_data(path_fac, ds_mask, time1, time2, mask_val)
    ds_cfac = read_data(path_cfac, ds_mask, time1, time2, mask_val)

    # Mean rainfall
    tp_fac = ds_fac['pr'].mean(dim="time") * 3600
    tp_cfac = ds_cfac['pr'].mean(dim="time") * 3600

    # Plot
    fig = plt.figure(figsize=(12, 4))
    gs = GridSpec(1, 3, figure=fig, width_ratios=[1, 1, 0.8])
    axs =[fig.add_subplot(1, 3, 1, projection=ccrs.PlateCarree()),
        fig.add_subplot(1, 3, 2, projection=ccrs.PlateCarree()),
        fig.add_subplot(1, 3, 3)]
    activate_geo(axs[0])
    activate_geo(axs[1])

    # Add precipitation color
    pcm = axs[0].pcolormesh(tp_fac.xlon, tp_fac.xlat, tp_fac, cmap=cmap, shading="auto",
        transform=ccrs.PlateCarree(), zorder=1, vmin=0, vmax=pr_max)
    axs[1].pcolormesh(tp_cfac.xlon, tp_cfac.xlat, tp_cfac, cmap=cmap, shading="auto",
        transform=ccrs.PlateCarree(), zorder=1, vmin=0, vmax=pr_max)

    # Add title
    axs[0].set_title('Factual')
    axs[1].set_title(f'Counterfactual')

    # Shared horizontal colorbar
    cbar = fig.colorbar(pcm, ax=axs[:2], orientation="horizontal", pad=0.08, fraction=0.06, aspect=40)
    cbar.set_label(unit)

    # Set extent
    set_extent(axs[0])
    set_extent(axs[1])

    # Histogram
    plot_density(axs[2], tp_fac, tp_cfac, pr_max, pr_min, unit)

    # Define cf ensemble
    exp_list = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']
    for exp in exp_list:

        path_cfac = cfac_path(exp)

        # Read file
        ds_cfac = read_data(path_cfac, ds_mask, time1, time2, mask_val)

        # Max rainfall
        tp_cfac = ds_cfac['pr'].mean(dim="time") * 3600

        # Histogram
        plot_density_simple(axs[2], tp_cfac, pr_min, pr_max, color='k', alpha=0.5)

    plt.tight_layout()
    fig.subplots_adjust(bottom=0.25, wspace=0.05)
    plt.savefig(outfile)
