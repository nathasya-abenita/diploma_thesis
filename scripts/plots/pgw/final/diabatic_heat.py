from mod_pgw import PGW

if __name__ == '__main__':
    # Create spatial map
    pgw = PGW(filename='ttenlsc_max.nc', val_min=0.0, val_max=0.03,
                         unit="Max. Temp. Tendency (Latent Heat Exchange) (K s⁻¹)",
                         var_name='ttenlsc', time_start="2025-11-25", time_end="2025-11-26",
                         time_stat='max', ens_stat='mean')
    # pgw.plot_map(outfile=r'./figs/compare/finals/map_diab.png')

    # Create distribution change graph
    pgw = PGW(filename='ttenlsc_max.nc', val_min=0, val_max=0.005,
                             unit="Max. Temp. Tendency (Latent Heat Exchange) (K s⁻¹)",
                             var_name='ttenlsc', time_start="2025-11-25", time_end="2025-11-26",
                             time_stat=None, ens_stat='mean')
    pgw.plot_dist_change(change_val_min=0.005, change_val_max=0.05,
                         change_min=-20, change_max=20, outfile=r'./figs/compare/finals/dist_diab')