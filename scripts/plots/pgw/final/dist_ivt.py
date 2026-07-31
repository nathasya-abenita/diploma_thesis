'''
pct=99
pct:  2961.9,  3398.5,  3708.8
pct_change:  10.0,  6.1
'''

from mod_pgw import *

def cfac_past_path(exp):
    return rf'./data/final_exp/counterfactual/GWL-1.5/{exp}/ivt_1000_700.nc'

def cfac_fut_path(exp):
    return rf'./data/final_exp/counterfactual/GWL+1.5/{exp}/ivt_1000_700.nc'

def compute_cfac_exceedance_prob(cfac_path, values_fac, case):
    model_list = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']
    values_cfac_list = []
    change_list = []
    
    # Plot members of counterfactual
    if cfac_path != None:
        for exp in model_list:
            path_cfac = cfac_path(exp)
            ds_cfac = read_data(path_cfac, time1, time2, rename=True)
            ds_cfac = cut_area(ds_cfac)
            pr_cfac = ds_cfac['ivt']

            excd_prob, values = compute_exceedance_prob(pr_cfac.values)
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
    outpath = './figs/compare/finals/dist_ivt.png'

    path_fac = r'./data/final_exp/factual/ivt_1000_700.nc'
    unit = r'Low-Level Integrated Vapor Transport (kg m s$^{-1}$)'

    # Read file
    ds_fac = read_data(path_fac, time1, time2, rename=True)
    ds_fac = cut_area(ds_fac)

    # Read precipitation value 
    pr_fac = ds_fac['ivt']

    # Set up plot
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))
    lw = 3
    pr_min, pr_max = 0, 1000
    # Compute factual
    excd_prob, values_fac = compute_exceedance_prob(pr_fac.values)    

    # Plot counterfactuals (past)
    excd_prob, ens_val_mean1, ens_val_std1, ens_change_mean1, ens_change_std1 = compute_cfac_exceedance_prob(cfac_past_path, values_fac, case='past')
    plot_cfac_exceedance_prob(axs[0], excd_prob, ens_val_mean1, ens_val_std1,
                              linewidth=lw, color='tab:blue', label='past -1.5K')
    plot_cfac_normal_plot(axs[1], ens_val_mean1, ens_change_mean1, ens_change_std1,
                                  linewidth=lw, color='tab:blue', label='past-present')
    # plot_density_simple(axs[2], ens_val_mean, pr_min=pr_min, pr_max=pr_max, color='tab:blue', linewidth=lw/2, label='past -1.5K')
    plot_hist_simple(axs[2], ens_val_mean1, pr_min=pr_min, pr_max=pr_max, color='tab:blue', alpha=0.25, label='past -1.5K')

    # Plot factual
    plot_exceedance_prob(axs[0], excd_prob, values_fac, linewidth=lw, color='k', label='present')
    # plot_density_simple(axs[2], values_fac, pr_min=pr_min, pr_max=pr_max, color='k', linestyle='--', linewidth=lw/2, label='present')
    plot_hist_simple(axs[2], values_fac, pr_min=pr_min, pr_max=pr_max, color='k', alpha=0.25, label='present')

    # Plot counterfactuals (future)
    excd_prob, ens_val_mean2, ens_val_std2, ens_change_mean2, ens_change_std2 = compute_cfac_exceedance_prob(cfac_fut_path, values_fac, case='fut.')
    plot_cfac_exceedance_prob(axs[0], excd_prob, ens_val_mean2, ens_val_std2,
                                linewidth=lw, color='tab:red', label='fut. +1.5K')
    plot_cfac_normal_plot(axs[1], values_fac, ens_change_mean2, ens_change_std2,
                                    linewidth=lw, color='tab:red', label='present-fut.')
    # plot_density_simple(axs[2], ens_val_mean, pr_min=pr_min, pr_max=pr_max, color='tab:red', linestyle=':', linewidth=lw/2, label='fut. +1.5K')
    plot_hist_simple(axs[2], ens_val_mean2, pr_min=pr_min, pr_max=pr_max, color='tab:red', alpha=0.25, label='fut. +1.5K')

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
    axs[1].set_xlim(pr_min, pr_max)
    axs[1].set_ylim(-10, 15)

    # Decorate plots
    axs[0].set_ylabel(unit)
    axs[0].set_xlabel('Exceedance Probability')
    axs[0].legend()
    
    axs[1].legend(ncols=1)
    axs[1].set_ylabel('Change per degree global\nwarming (% K$^{-1}$)')
    axs[1].set_xlabel(unit)

    axs[2].legend()
    axs[2].set_ylabel('Density')
    axs[2].set_xlabel(unit)
    plt.tight_layout()
    plt.savefig(outpath)

    # Extract percentile
    idx = np.searchsorted(excd_prob[::-1], 0.01)
    pct_present = values_fac[-idx-1]
    pct_past = ens_val_mean1[-idx-1]
    pct_fut = ens_val_mean2[-idx-1]
    pct_past_present_change = ens_change_mean1[-idx-1]
    pct_present_fut_change = ens_change_mean2[-idx-1]

    print(f'pct: {pct_past: .1f}, {pct_present: .1f}, {pct_fut: .1f}')
    print(f'pct_change: {pct_past_present_change: .1f}, {pct_present_fut_change: .1f}')