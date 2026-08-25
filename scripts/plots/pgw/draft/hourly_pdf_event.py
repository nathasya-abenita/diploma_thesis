from scripts.plots.pgw.draft.mod_prec import *

def cfac_path(exp):
    return rf'./data/final_exp/counterfactual/GWL-1.5/{exp}/pr_SRF.nc'

if __name__ == '__main__':
    time1, time2 = '2025-11-25', '2025-11-26'

    # Define paths
    path_fac = r'./data/final_exp/factual/pr_SRF.nc'
    path_cfac = cfac_path('ensemble')
    path_mask = r'./data/shp/mask_aceh.nc' #r'./data/counterfactual/mask_SRF.nc'
    mask_val = 1 # 2
    unit = r'Precipitation (mm h$^{-1}$)'
    outpath = './figs/compare/hourly_pdf_event.png'

    # Read file
    ds_mask = cut_area(xr.open_dataset(path_mask))
    ds_fac = read_data(path_fac, ds_mask, time1, time2, mask_val)
    ds_cfac = read_data(path_cfac, ds_mask, time1, time2, mask_val)

    # Read precipitation value (mm/s) to (mm/hr) 
    pr_fac = ds_fac['pr'] * 3600
    pr_cfac = ds_cfac['pr'] * 3600

    # Parameters on precipitation value
    pr_min, pr_max = 0, 20
    exp_list = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']

    # Plot
    fig, ax = plt.subplots()
    
    # ax.set_title()
    print(pr_fac.sel(time=slice(time1, time2)))
    plot_density_simple(ax, pr_fac.sel(time=slice(time1, time2)), pr_min, pr_max, linewidth=4, color='tab:blue', label='factual')
    plot_density_simple(ax, pr_cfac.sel(time=slice(time1, time2)), pr_min, pr_max, linewidth=4, color='k', label='counterfactual')
    
    for exp in exp_list:
        path_cfac = path_cfac = cfac_path(exp)
        ds_cfac = read_data(path_cfac, ds_mask, time1, time2, mask_val)
        pr_cfac = ds_cfac['pr'] * 3600
        plot_density_simple(ax, pr_cfac.sel(time=slice(time1, time2)), pr_min, pr_max, color='gray')
    
    ax.set_xlabel(unit)
    ax.set_ylabel("Density")
    ax.legend()
    ax.set_title(f'Peak event: {time1} to {time2}')
    
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath)