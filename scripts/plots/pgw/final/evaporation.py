from mod_pgw import PGW

if __name__ == '__main__':
    # Create spatial map
    fun = lambda x : x * 1_000
    pgw = PGW(filename='evspsbl_SRF.nc', val_min=0, val_max=0.095, val_modify_func=fun,
                        unit=r"Evaporation Flux (mm s$^{-1}$)",
                        var_name='evspsbl', time_start="2025-11-25", time_end="2025-11-26",
                        time_stat='mean', ens_stat='mean')
    # pgw.plot_map(outfile=r'./figs/compare/finals/map_evs.png')

    # Create distribution change graph
    pgw = PGW(filename='evspsbl_SRF.nc', val_min=0.02, val_max=0.2, val_modify_func=fun,
                            unit=r"Evaporation Flux (mm s$^{-1}$)",
                            var_name='evspsbl', time_start="2025-11-25", time_end="2025-11-26",
                            time_stat=None, ens_stat='mean')
    pgw.plot_dist_change(change_val_min=0.02, change_val_max=0.2, ylim_pdf=(1e-4, 1e2),
                         change_min=-5, change_max=15, outfile=r'./figs/compare/finals/dist_evs')