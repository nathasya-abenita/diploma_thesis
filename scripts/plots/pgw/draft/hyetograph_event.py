from scripts.plots.pgw.draft.mod_prec import *

def plot_hyetograph (ax, pr : xr.DataArray,
                     color=None, alpha=1, linewidth=None, label=None, linestyle=None):
    pr_array = np.nanmean(pr.values, axis=(1, 2))
    ax.plot(pr.time, pr_array, color=color, alpha=alpha, linewidth=linewidth, label=label, linestyle=linestyle)

def plot_cum_hyetograph (ax, pr : xr.DataArray,
                     color=None, alpha=1, linewidth=None, label=None, linestyle=None):
    pr_array = np.nanmean(pr.values, axis=(1, 2))
    ax.plot(pr.time, np.cumsum(pr_array), color=color, alpha=alpha, linewidth=linewidth, label=label, linestyle=linestyle)

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
    outpath = './figs/compare/hyetograph_event.png'

    # Read file
    ds_mask = cut_area(xr.open_dataset(path_mask))
    ds_fac = read_data(path_fac, ds_mask, time1, time2, mask_val)
    ds_cfac = read_data(path_cfac, ds_mask, time1, time2, mask_val)
    print(ds_cfac.time)

    # Read precipitation value (mm/s) to (mm/hr) 
    pr_fac = ds_fac['pr'] * 3600
    pr_cfac = ds_cfac['pr'] * 3600

    # Parameters on precipitation value
    pr_min, pr_max = 0, 20
    exp_list = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']
    exp_ls_list = ['-', '-.', ':', '--']

    # Set up plot
    fig, axs = plt.subplots(2, 1, sharex=True, figsize=(9, 6))
    
    # Plot factual and ensemble of counterfactual
    lw = 2
    plot_hyetograph(axs[0], pr_fac, linewidth=lw, color='tab:blue', label='factual')
    plot_hyetograph(axs[0], pr_cfac, linewidth=lw, color='k', label='counterfactual')
    plot_cum_hyetograph(axs[1], pr_fac, linewidth=lw, color='tab:blue', label='factual')
    plot_cum_hyetograph(axs[1], pr_cfac, linewidth=lw, color='k', label='counterfactual')

    # Plot members of counterfactual
    for exp, ls in zip(exp_list, exp_ls_list):
        path_cfac = path_cfac = cfac_path(exp)
        ds_cfac = read_data(path_cfac, ds_mask, time1, time2, mask_val)
        pr_cfac = ds_cfac['pr'] * 3600
        plot_hyetograph(axs[0], pr_cfac, color='k', alpha=0.5, linestyle=ls, label=exp)
        plot_cum_hyetograph(axs[1], pr_cfac, color='k', alpha=0.5, linestyle=ls, label=exp)

    # Decorate plots
    axs[0].set_ylabel(unit)
    leg = axs[0].legend()
    # leg.get_frame().set_alpha(0.3)
    
    axs[1].legend()
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel(f'Cumulative Rainfall (mm)')
    plt.tight_layout()
    plt.savefig(outpath)