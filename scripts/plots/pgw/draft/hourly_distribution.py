from scripts.plots.pgw.draft.mod_prec import *

def cfac_path(exp : str):
    return rf'./data/final_exp/counterfactual/GWL-1.5/{exp}/pr_SRF.nc'

if __name__ == '__main__':
    time1, time2 = '2025-11-25', '2025-11-26'

    # Define paths
    path_fac = r'./data/final_exp/factual/pr_SRF.nc'
    path_cfac = cfac_path('ensemble')
    path_mask = r'./data/shp/mask_aceh.nc' #r'./data/counterfactual/mask_SRF.nc'
    mask_val = 1 # 2
    unit = r'Precipitation (mm h$^{-1}$)'
    outpath = './figs/compare/distribution_event.png'

    # Read file
    ds_mask = cut_area(xr.open_dataset(path_mask))
    ds_fac = read_data(path_fac, ds_mask, time1, time2, mask_val)
    ds_cfac = read_data(path_cfac, ds_mask, time1, time2, mask_val)

    # Read precipitation value (mm/s) to (mm/hr) 
    pr_fac = ds_fac['pr'] * 3600
    pr_cfac = ds_cfac['pr'] * 3600

    # Parameters on precipitation value
    pr_min, pr_max = 0, 15
    exp_list = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']
    exp_ls_list = ['-', '-.', ':', '--']

    # Set up plot
    fig, axs = plt.subplots(2, 1, figsize=(8, 8))
    
    # Plot factual
    lw = 4
    plot_hist_simple(axs[0], pr_fac, pr_min, pr_max, color='tab:blue', label='factual', alpha=0.5)
    plot_exceedance_prob(axs[1], pr_fac, linewidth=lw, color='tab:blue', label='factual')

    # Plot ensemble of counterfactual
    plot_hist_simple(axs[0], pr_cfac, pr_min, pr_max, color='k', label='counterfactual', alpha=0.5)
    plot_exceedance_prob(axs[1], pr_cfac, color='k', alpha=1, label='counterfactual', linewidth=lw)
    
    # Plot members of counterfactual
    for exp, ls in zip(exp_list, exp_ls_list):
        path_cfac = cfac_path(exp)
        ds_cfac = read_data(path_cfac, ds_mask, time1, time2, mask_val)
        pr_cfac = ds_cfac['pr'] * 3600

        # plot_hist_simple(axs[0], pr_cfac, pr_min, pr_max, alpha=1, color='k')
        plot_exceedance_prob(axs[1], pr_cfac, alpha=1, color='k', linestyle=ls, label=exp)


    
    # Decorate plots
    axs[0].set_xlabel(unit)
    axs[0].set_ylabel('Density')
    axs[0].legend()
    
    axs[1].legend()
    axs[1].set_ylabel(unit)
    axs[1].set_xlabel('Exceedance Probability')
    plt.tight_layout()
    plt.savefig(outpath)