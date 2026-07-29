from mod_pgw import *

def cfac_past_path(exp):
    return rf'./data/final_exp/counterfactual/GWL-1.5/{exp}/pr_SRF.nc'

def cfac_fut_path(exp):
    return rf'./data/final_exp/counterfactual/GWL+1.5/{exp}/pr_SRF.nc'

def compute_cfac_exceedance_prob(cfac_path, values_fac, case):
    model_list = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']
    values_cfac_list = []
    change_list = []
    
    # Plot members of counterfactual
    if cfac_path != None:
        for exp in model_list:
            path_cfac = cfac_path(exp)
            ds_cfac = read_data(path_cfac, time1, time2)
            ds_cfac = mask_data(ds_cfac, ds_mask)
            pr_cfac = ds_cfac['pr'] * 3600

            excd_prob, values = compute_exceedance_prob(pr_cfac)
            values_cfac_list.append(values)

            if case == 'past':
                change = (values_fac - values) / values * 100
            elif case == 'fut.':
                change = (values - values_fac) / values_fac * 100
            else:
                raise ValueError ('check case again!')
            change_list.append(change / 1.5) # convert unit to % per degree
 
    # Compute ensemble stats
    stacked_val = np.stack(values_cfac_list)      # shape: (n_ens, n_points)
    stacked_change = np.stack(change_list)

    # ens_mean = np.median(stacked, axis=0)
    ens_val_mean = stacked_val.mean(axis=0)
    ens_val_std  = stacked_val.std(axis=0)
    ens_change_mean = stacked_change.mean(axis=0)
    ens_change_std = stacked_change.std(axis=0)
    return excd_prob, ens_val_mean, ens_val_std, ens_change_mean, ens_change_std

def plot_cfac_exceedance_prob(ax, excd_prob, ens_mean, ens_std, linewidth=None, color=None, label=None):
    plot_exceedance_prob(ax, excd_prob, ens_mean, linewidth=linewidth, color=color, label=label)
    ax.fill_between(excd_prob, ens_mean - ens_std, ens_mean + ens_std, 
                    color=color, alpha=0.2, edgecolor=None)

def plot_cfac_normal_plot(ax, values, ens_mean, ens_std, linewidth=None, color=None, label=None):
    ax.plot(values, ens_mean, linewidth=linewidth, color=color, label=label)
    ax.fill_between(values, ens_mean - ens_std, ens_mean + ens_std, 
                    color=color, alpha=0.2, edgecolor=None)


if __name__ == '__main__':
    time1, time2 = '2025-11-25', '2025-11-26'

    # Define paths
    outpath = './figs/compare/finals/dist_pr.png'

    path_fac = r'./data/final_exp/factual/pr_SRF.nc'
    path_mask = r'./data/shp/mask_aceh.nc' #r'./data/counterfactual/mask_SRF.nc'
    mask_val = 1 
    unit = r'Precipitation (mm h$^{-1}$)'

    # Read file
    ds_mask = cut_area(xr.open_dataset(path_mask))
    ds_fac = read_data(path_fac, time1, time2)
    ds_fac = mask_data(ds_fac, ds_mask)

    # Read precipitation value (mm/s) to (mm/hr) 
    pr_fac = ds_fac['pr'] * 3600

    # Set up plot
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))
    lw = 3
    pr_min, pr_max = 0, 20
    # Compute factual
    excd_prob, values_fac = compute_exceedance_prob(pr_fac)    

    # Plot counterfactuals (past)
    excd_prob, ens_val_mean, ens_val_std, ens_change_mean1, ens_change_std1 = compute_cfac_exceedance_prob(cfac_past_path, values_fac, case='past')
    plot_cfac_exceedance_prob(axs[0], excd_prob, ens_val_mean, ens_val_std,
                              linewidth=lw, color='tab:blue', label='past -1.5K')
    plot_cfac_normal_plot(axs[1], ens_val_mean, ens_change_mean1, ens_change_std1,
                                  linewidth=lw, color='tab:blue', label='past -1.5K')
    plot_density_simple(axs[2], ens_val_mean, pr_min=pr_min, pr_max=pr_max, color='tab:blue', linewidth=lw/2, label='past -1.5K')

    # Plot factual
    plot_exceedance_prob(axs[0], excd_prob, values_fac, linewidth=lw, color='k', label='present')
    plot_density_simple(axs[2], values_fac, pr_min=pr_min, pr_max=pr_max, color='k', linewidth=lw/2, label='present')

    # Plot counterfactuals (future)
    excd_prob, ens_val_mean, ens_val_std, ens_change_mean2, ens_change_std2 = compute_cfac_exceedance_prob(cfac_fut_path, values_fac, case='fut.')
    plot_cfac_exceedance_prob(axs[0], excd_prob, ens_val_mean, ens_val_std,
                                linewidth=lw, color='tab:red', label='fut. +1.5K')
    plot_cfac_normal_plot(axs[1], values_fac, ens_change_mean2, ens_change_std2,
                                    linewidth=lw, color='tab:red', label='fut. +1.5K')
    plot_density_simple(axs[2], ens_val_mean, pr_min=pr_min, pr_max=pr_max, color='tab:red', linewidth=lw/2, label='fut. +1.5K')

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

    # axs[1].set_xlim(0.5, 1e-6)
    axs[1].set_xlim(10, 100)
    axs[1].set_ylim(-10, 30)
    plot_limit_change(axs[1], x1=10, x2=100)

    # Decorate plots
    axs[0].set_ylabel(unit)
    axs[0].set_xlabel('Exceedance Probability')
    axs[0].legend()
    
    axs[1].legend(ncols=2)
    axs[1].set_ylabel('Change per degree global\nwarming (% K$^{-1}$)')
    axs[1].set_xlabel(unit)

    axs[2].legend()
    axs[2].set_ylabel('Density')
    axs[2].set_xlabel(unit)
    plt.tight_layout()
    plt.savefig(outpath)