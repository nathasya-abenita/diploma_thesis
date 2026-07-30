'''
delivarables:
1) median change of accumulated precipitation

past to the present: +10.02%
present to the future: -8.97%

2) median change of rainfall area (pct 90)
past to present (area of precipitation): 78.13
past to present (area of precipitation): 63.89

median change of rainfall area (300 mm / 2 day)
past to present (area of precipitation): 78.13
present to future (area of precipitation): -14.62

'''

from mod_pgw import *

def cfac_past_path(exp):
    return rf'./data/final_exp/counterfactual/GWL-1.5/{exp}/pr_SRF.nc'

def cfac_fut_path(exp):
    return rf'./data/final_exp/counterfactual/GWL+1.5/{exp}/pr_SRF.nc'

def compute_fldmean(da : xr.DataArray):
    return np.nanmean(da.values)

def compute_grids_above_thr (values : np.array , thr : float):
    values = values.flatten()
    values = values[~np.isnan(values)]
    return (values > thr).mean()

def compute_pct(values, pct):
    values = values.flatten()
    values = values[~np.isnan(values)]
    return np.percentile(values, pct)

def compute_change(cfac_path : callable, acc_fac : float, n_fac : int, pct_fac : float, case : str):
    exp_list = ['tweak', 'EC-Earth3-Veg', 'MPI-ESM1-2-HR', 'NorESM2-MM']
    change_list = []
    n_change_list = []
    for exp in exp_list:
        # Define path
        path_cfac = cfac_path(exp)
        # Read file
        ds_cfac = read_data(path_cfac, time1, time2)
        ds_cfac = mask_data(ds_cfac, ds_mask)
        # Accumulated rainfall
        tp_cfac = ds_cfac['pr'].sum(dim="time", skipna=False) * 3600
        acc_cfac = compute_fldmean(tp_cfac)
        n_cfac = compute_grids_above_thr(tp_cfac.values, pct_fac)
        # Compute change
        if case == 'fut.':
            change = (acc_cfac - acc_fac) / acc_fac * 100
            n_change = (n_cfac - n_fac) / n_fac * 100
        elif case == 'past':
            change = (acc_fac - acc_cfac) / acc_cfac * 100
            n_change = (n_fac - n_cfac) / n_cfac * 100
        else:
            raise ValueError ('check case option!')
        change_list.append(change)
        n_change_list.append(n_change)

    print(n_change_list)
    return np.median(change_list), np.median(n_change_list)

if __name__ == '__main__':
    # Parameters
    stat = 'mean'

    time1, time2 = "2025-11-25", "2025-11-26"
    pr_max = 180 * 4
    pr_min = 0 # pr_max / 15 # divided by nlevel
    unit = r"Accumulated precipitation 25-26Nov2025 (mm)"
    path_mask = r'./data/shp/mask_aceh.nc'

    # Compute for factual
    ds_mask = cut_area(xr.open_dataset(path_mask))
    path_fac = r'./data/final_exp/factual/pr_SRF.nc'
    ds_fac = read_data(path_fac, time1, time2)
    ds_fac = mask_data(ds_fac, ds_mask)
    tp_fac = ds_fac['pr'].sum(dim="time", skipna=False) * 3600
    # Compute extremes
    pct_fac = 300 # compute_pct(tp_fac.values, 99)
    n_fac = compute_grids_above_thr(tp_fac.values, pct_fac)
    print(pct_fac)

    # fig, ax = plt.subplots()
    # tp_fac.plot(ax=ax); plt.show()
    acc_fac = compute_fldmean(tp_fac)
    # print(acc_fac)

    # Compute for past to present
    change, n_change = compute_change(cfac_past_path, acc_fac, n_fac, pct_fac, case='past')
    print('past to present (total precipitation):', f'{change:.2f}')
    print('past to present (area of precipitation):', f'{n_change:.2f}')

    # Compute for present to future
    change, n_change = compute_change(cfac_fut_path, acc_fac, n_fac, pct_fac, case='fut.')
    print('present to future (total precipitation):', f'{change:.2f}')
    print('present to future (area of precipitation):', f'{n_change:.2f}')
