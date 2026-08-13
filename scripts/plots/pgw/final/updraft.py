from mod_pgw import PGW

if __name__ == '__main__':
    # Create spatial map
    pgw = PGW(filename='wa_max.nc', val_min=0, val_max=10,
                        unit=r"Maximum Vertical Velocity (m s$^{-1}$)",
                        var_name='wa', time_start="2025-11-25", time_end="2025-11-28",
                        time_stat='max', ens_stat='mean')
    pgw.plot_map(outfile=r'./figs/compare/finals/map_wa.png')

    # Create distribution change graph
    pgw = PGW(filename='wa_max.nc', val_min=0, val_max=1,
                            unit=r"Maximum Vertical Velocity (m s$^{-1}$)",
                            var_name='wa', time_start="2025-11-25", time_end="2025-11-26",
                            time_stat=None, ens_stat='mean')
    pgw.plot_dist_change(change_val_min=0.5, change_val_max=5,
                         change_min=0, change_max=17.5, outfile=r'./figs/compare/finals/dist_wa')