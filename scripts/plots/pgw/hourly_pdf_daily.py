from mod_prec import *

def cfac_path(exp, direction='-'):
    return rf'./data/final_exp/counterfactual/GWL{direction}1.5/{exp}/pr_SRF.nc'

if __name__ == '__main__':
    time_list = ['2025-11-25', '2025-11-26', '2025-11-27', '2025-11-28']

    # Define paths
    exp = 'ensemble'
    path_fac = r'./data/final_exp/factual/pr_SRF.nc'
    path_cfac = cfac_path(exp)
    path_mask = r'./data/shp/mask_aceh.nc' #r'./data/counterfactual/mask_SRF.nc'
    mask_val = 1 # 2
    outpath = './figs/compare/hourly_pdf_daily.png'
    unit = r'Precipitation (mm h$^{-1}$)'

    # Read file
    ds_mask = cut_area(xr.open_dataset(path_mask))
    ds_fac = read_data(path_fac, ds_mask, time_list[0], time_list[-1], mask_val)
    ds_cfac = read_data(path_cfac, ds_mask, time_list[0], time_list[-1], mask_val)

    # Read precipitation value (mm/s) to (mm/hr) 
    pr_fac = ds_fac['pr'] * 3600
    pr_cfac = ds_cfac['pr'] * 3600

    # Parameters on precipitation value
    pr_min, pr_max = 0, 4
    exp_list = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']

    # Plot
    fig, axs = plt.subplots(4, 1, figsize=(12,9), sharey=True)
    
    for i, time in enumerate(time_list):
        axs[i].set_title(time)
        print(pr_fac.sel(time=slice(time, time)))
        plot_density_simple(axs[i], pr_fac.sel(time=slice(time, time)), pr_min, pr_max, linewidth=4, color='tab:blue')
        plot_density_simple(axs[i], pr_cfac.sel(time=slice(time, time)), pr_min, pr_max, linewidth=4, color='k')
        axs[i].set_xlabel(unit)
        axs[i].set_ylabel("Density")
        axs[i].legend()

    for exp in exp_list:
        path_cfac = path_cfac = cfac_path(exp)
        ds_cfac = read_data(path_cfac, ds_mask, time_list[0], time_list[-1], mask_val)
        pr_cfac = ds_cfac['pr'] * 3600
        for i, time in enumerate(time_list):
            plot_density_simple(axs[i], pr_cfac.sel(time=slice(time, time)), pr_min, pr_max, alpha=0.1, color='gray')
    plt.tight_layout()
    plt.savefig(outpath)