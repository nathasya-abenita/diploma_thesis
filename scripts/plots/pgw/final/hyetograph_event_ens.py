from mod_pgw import *

def cfac_past_path(exp):
    return rf'./data/final_exp/counterfactual/GWL-1.5/{exp}/pr_SRF.nc'

def cfac_fut_path(exp):
    return rf'./data/final_exp/counterfactual/GWL+1.5/{exp}/pr_SRF.nc'

def compute_fldmean(pr : xr.DataArray):
    return np.nanmean(pr.values, axis=(1, 2)) # axis of lon and lat

def plot_hyetograph (ax, datetime, pr_array : np.array,
                     std_array=None, color=None, alpha=1, linewidth=None, label=None, linestyle=None):
    # pr_array = np.nanmean(pr.values, axis=(1, 2))
    if std_array is None:
        ax.plot(datetime, pr_array, color=color, alpha=alpha, linewidth=linewidth, label=label, linestyle=linestyle)
    else:
        ax.fill_between(datetime, pr_array - std_array, pr_array + std_array, 
                        alpha=alpha, color=color, edgecolor=None,)

def plot_cum_hyetograph (ax, datetime, pr_array, std_array=None,
                     color=None, alpha=1, linewidth=None, label=None, linestyle=None):
    if std_array is None:
        ax.plot(datetime, np.cumsum(pr_array), color=color, alpha=alpha, linewidth=linewidth, label=label, linestyle=linestyle)
    else:
        ax.fill_between(datetime, np.cumsum(pr_array - std_array), np.cumsum(pr_array + std_array),
                        alpha=alpha, color=color, edgecolor=None, )
        
if __name__ == '__main__':
    time1, time2 = '2025-11-25', '2025-11-26'

    # Define paths
    outpath = './figs/compare/finals/hyetograph_event_ensmedian.png'
    path_fac = r'./data/final_exp/factual/pr_SRF.nc'
    path_mask = r'./data/shp/mask_aceh.nc' #r'./data/counterfactual/mask_SRF.nc'
    unit = r'Precipitation (mm h$^{-1}$)'
    ens_stat = 'median' # 'median' or 'mean'

    # Read file
    ds_mask = cut_area(xr.open_dataset(path_mask))
    ds_fac = read_data(path_fac, time1, time2)
    ds_fac = mask_data(ds_fac, ds_mask)

    # Read precipitation value (mm/s) to (mm/hr) 
    pr_fac = ds_fac['pr'] * 3600

    # Parameters on precipitation value
    pr_min, pr_max = 0, 20
    exp_list = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']

    # Set up plot
    fig, axs = plt.subplots(2, 1, sharex=True, figsize=(9, 6))
    lw = 2

    # Compute counterfactual (past)
    pr_cfac_list = []
    for exp in exp_list:
        path_cfac = cfac_past_path(exp)
        ds_cfac = read_data(path_cfac, time1, time2)
        ds_cfac = mask_data(ds_cfac, ds_mask)
        pr_cfac = ds_cfac['pr'] * 3600
        pr_cfac_list.append(compute_fldmean(pr_cfac))
    if ens_stat == 'mean':
        ens_pr_mean, ens_pr_std = compute_ens_mean_std(pr_cfac_list)
    elif ens_stat == 'median':
        ens_pr_mean, ens_pr_std = compute_ens_med_std(pr_cfac_list)
    else:
        raise ValueError ('check `ens_stat` option!')

    plot_hyetograph(axs[0], pr_cfac.time, ens_pr_mean,
                    color='tab:blue', label='past -1.5K')
    plot_cum_hyetograph(axs[1], pr_cfac.time, ens_pr_mean,
                        color='tab:blue', label='past -1.5K')

    plot_hyetograph(axs[0], pr_cfac.time, ens_pr_mean, std_array=ens_pr_std,
                    color='tab:blue', alpha=0.2)
    plot_cum_hyetograph(axs[1], pr_cfac.time, ens_pr_mean, std_array=ens_pr_std,
                        color='tab:blue', alpha=0.2)

    # Plot factual and ensemble of counterfactual
    plot_hyetograph(axs[0], pr_fac.time, compute_fldmean(pr_fac), 
                    linewidth=lw, color='k', label='factual')
    plot_cum_hyetograph(axs[1], pr_fac.time, compute_fldmean(pr_fac), 
                        linewidth=lw, color='k', label='factual')

    # Compute counterfactual (future)
    pr_cfac_list = []
    for exp in exp_list:
        path_cfac = cfac_fut_path(exp)
        ds_cfac = read_data(path_cfac, time1, time2)
        ds_cfac = mask_data(ds_cfac, ds_mask)
        pr_cfac = ds_cfac['pr'] * 3600
        pr_cfac_list.append(compute_fldmean(pr_cfac))
    ens_pr_mean, ens_pr_std = compute_ens_mean_std(pr_cfac_list)

    plot_hyetograph(axs[0], pr_cfac.time, ens_pr_mean,
                    color='tab:red', label='fut. +1.5K')
    plot_cum_hyetograph(axs[1], pr_cfac.time, ens_pr_mean,
                        color='tab:red', label='fut. +1.5K')

    plot_hyetograph(axs[0], pr_cfac.time, ens_pr_mean, std_array=ens_pr_std,
                    color='tab:red', alpha=0.2)
    plot_cum_hyetograph(axs[1], pr_cfac.time, ens_pr_mean, std_array=ens_pr_std,
                        color='tab:red', alpha=0.2)

    # Decorate plots
    axs[0].set_ylabel(unit)
    leg = axs[0].legend()
    # leg.get_frame().set_alpha(0.3)
    
    axs[1].legend()
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel(f'Cumulative Rainfall (mm)')
    plt.tight_layout()
    plt.savefig(outpath)