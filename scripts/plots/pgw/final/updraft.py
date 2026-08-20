from mod_pgw import PGW
import numpy as np

if __name__ == '__main__':
    # Create spatial map
    pgw = PGW(filename='wa_max.nc', val_min=0, val_max=10,
                        unit=r"Maximum Vertical Velocity (m s$^{-1}$)",
                        var_name='wa', time_start="2025-11-25", time_end="2025-11-28",
                        time_stat='max', ens_stat='max')
    # pgw.plot_map(outfile=r'./figs/compare/finals/map_wa_max.png')

    # Create distribution change graph
    pgw = PGW(filename='wa_max.nc', val_min=0, val_max=1,
                            unit=r"Maximum Vertical Velocity (m s$^{-1}$)",
                            var_name='wa', time_start="2025-11-25", time_end="2025-11-26",
                            time_stat=None, ens_stat='mean')
    pgw.plot_dist_change(change_val_min=0.5, change_val_max=5, pct=99.9, ylim_pdf=(1e-7, 1), bins=np.arange(0, 40, 0.25),
                         change_min=0, change_max=15, outfile=r'./figs/compare/finals/dist_wa')