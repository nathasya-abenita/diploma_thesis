from mod_pgw import *

def cfac_past_path(exp):
    return rf'./data/final_exp/counterfactual/GWL-1.5/{exp}/ttenlsc_max.nc'

def cfac_fut_path(exp):
    return rf'./data/final_exp/counterfactual/GWL+1.5/{exp}/ttenlsc_max.nc'

def compute_fldmean(da : xr.DataArray):
    return np.nanmean(da.values)

def compute_grids_above_thr (values : np.array , thr : float):
    values = values.flatten()
    values = values[~np.isnan(values)]
    return (values > thr).sum()

def compute_pct(values, pct):
    values = values.flatten()
    values = values[~np.isnan(values)]
    return np.percentile(values, pct)

def compute_change(cfac_path : callable, n_fac : int, pct_fac : float, case : str):
    exp_list = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']
    n_change_list = []
    for exp in exp_list:
        # Define path
        path_cfac = cfac_path(exp)
        # Read file
        ds_cfac = read_data(path_cfac, time1, time2)
        # Take time max
        tp_cfac = ds_cfac['ttenlsc'].max(dim="time", skipna=False)
        n_cfac = compute_grids_above_thr(tp_cfac.values, pct_fac)
        # Compute change
        if case == 'fut.':
            n_change = (n_cfac - n_fac) / n_fac * 100
        elif case == 'past':
            n_change = (n_fac - n_cfac) / n_cfac * 100
        else:
            raise ValueError ('check case option!')
        n_change_list.append(n_change)

    print(n_change_list)
    return np.median(n_change_list)

# def compute_change(cfac_path : callable, n_fac : int, pct_fac : float, case : str):
#     exp_list = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']
#     pr_list = []
#     for exp in exp_list:
#         # Define path
#         path_cfac = cfac_path(exp)
#         # Read file
#         ds_cfac = read_data(path_cfac, time1, time2)
#         # Take time max
#         tp_cfac = ds_cfac['ttenlsc'].max(dim="time", skipna=False)
#         pr_list.append(tp_cfac)
#     ens_pr_mean, _ = compute_ens_mean_std(pr_list)
#     n_cfac = compute_grids_above_thr(ens_pr_mean, pct_fac)
#     # Compute change
#     if case == 'fut.':
#         n_change = (n_cfac - n_fac) / n_fac * 100
#     elif case == 'past':
#         n_change = (n_fac - n_cfac) / n_cfac * 100
#     else:
#         raise ValueError ('check case option!')
    
#     return n_change

if __name__ == '__main__':
    # Parameters
    time1, time2 = "2025-11-25", "2025-11-26"

    # Compute for factual
    path_fac = r'./data/final_exp/factual/ttenlsc_max.nc'
    ds_fac = read_data(path_fac, time1, time2)
    tp_fac = ds_fac['ttenlsc'].max(dim="time", skipna=False)
    # Compute extremes
    pct_fac = 0.009 # compute_pct(tp_fac.values, 99)
    n_fac = compute_grids_above_thr(tp_fac.values, pct_fac)
    print(pct_fac)

    # Compute for past to present
    n_change = compute_change(cfac_past_path, n_fac, pct_fac, case='past')
    print('past to present (area):', f'{n_change:.2f}')

    # Compute for present to future
    n_change = compute_change(cfac_fut_path, n_fac, pct_fac, case='fut.')
    print('present to future (area):', f'{n_change:.2f}')
