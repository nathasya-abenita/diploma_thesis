from mod_pgw import PGW

if __name__ == '__main__':
    # Create spatial map
    pgw = PGW(filename='cape_SRF.nc', val_min=0, val_max=2_500,
                        unit=r"CAPE (J kg$^{-1}$)",
                        var_name='cape', time_start="2025-11-25", time_end="2025-11-26",
                        time_stat='mean', ens_stat='mean')
    # pgw.plot_map(outfile=r'./figs/compare/finals/map_cape.png', cbar_n_level=20)

    # Create distribution change graph
    pgw = PGW(filename='cape_SRF.nc', val_min=0, val_max=3_000,
                        unit=r"CAPE (J kg$^{-1}$)",
                        var_name='cape', time_start="2025-11-25", time_end="2025-11-26",
                        time_stat=None, ens_stat='mean')
    pgw.plot_dist_change(change_val_min=200, change_val_max=3_000, ylim_pdf=(1e-7, 1e-1),
                         change_min=0, change_max=20, outfile=r'./figs/compare/finals/dist_cape')