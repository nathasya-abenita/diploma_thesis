from mod_pgw import PGW

if __name__ == '__main__':
    mod_pr = lambda da : da * 3_600 # mm / s to mm / hr

    # Create spatial map
    # pgw = PGW(filename='pr_SRF.nc', val_min=0, val_max=680, val_modify_func=mod_pr, mask=True,
    #                     unit=r"Accumulated precipitation 25-26Nov2025 (mm)",
    #                     var_name='pr', time_start="2025-11-25", time_end="2025-11-26",
    #                     time_stat='sum', ens_stat='mean')
    # pgw.plot_map(outfile=r'./figs/compare/finals/map_pr_mean.png')

    # pgw = PGW(filename='pr_SRF.nc', val_min=0, val_max=680, val_modify_func=mod_pr, mask=True,
    #                         unit=r"Accumulated precipitation 25-26Nov2025 (mm)",
    #                         var_name='pr', time_start="2025-11-25", time_end="2025-11-26",
    #                         time_stat='sum', ens_stat='median')
    # pgw.plot_map(outfile=r'./figs/compare/finals/map_pr_median.png')

    # pgw = PGW(filename='pr_SRF.nc', val_min=0, val_max=680, val_modify_func=mod_pr, mask=True,
    #                             unit=r"Accumulated precipitation 25-26Nov2025 (mm)",
    #                             var_name='pr', time_start="2025-11-25", time_end="2025-11-26",
    #                             time_stat='sum', ens_stat='max')
    # pgw.plot_map(outfile=r'./figs/compare/finals/map_pr_max.png')

    # Create distribution change graph
    pgw = PGW(filename='pr_SRF.nc', val_min=0, val_max=10, val_modify_func=mod_pr, mask=True,
            unit=r'Precipitation (mm h$^{-1}$)',
            var_name='pr', time_start="2025-11-25", time_end="2025-11-26",
            time_stat=None, ens_stat='mean')
    
    pgw.plot_dist_change(change_val_min=5, change_val_max=100, add_cc_limit=True,
                         change_min=-10, change_max=30, outfile=r'./figs/compare/finals/dist_pr_mean')

    pgw = PGW(filename='pr_SRF.nc', val_min=0, val_max=10, val_modify_func=mod_pr, mask=True,
                unit=r'Precipitation (mm h$^{-1}$)',
                var_name='pr', time_start="2025-11-25", time_end="2025-11-26",
                time_stat=None, ens_stat='median')
        
    pgw.plot_dist_change(change_val_min=5, change_val_max=100, add_cc_limit=True,
                             change_min=-10, change_max=30, outfile=r'./figs/compare/finals/dist_pr_median')