from mod_pgw import PGW
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # Create spatial map
    pgw = PGW(filename='ivt_1000_700.nc', rename=True, val_min=0, val_max=800,
                        unit=r"Low-Level Integrated Vapor Transport (kg m s$^{-1}$)",
                        var_name='ivt', time_start="2025-11-25", time_end="2025-11-26",
                        time_stat='mean', ens_stat='mean')
    # pgw.plot_map(outfile=r'./figs/compare/finals/map_ivt.png')

    # Create distribution change graph
    # pgw = PGW(filename='ivt_1000_700.nc', rename=True, val_min=0, val_max=100,
    #                     unit=r"Low-Level Integrated Vapor Transport (kg m s$^{-1}$)",
    #                     var_name='ivt', time_start="2025-11-25", time_end="2025-11-26",
    #                     time_stat=None, ens_stat='mean')
    # fig, axs = pgw.plot_dist_change(change_val_min=10, change_val_max=1_000,
    #                      change_min=-10, change_max=15, outfile=r'./figs/compare/finals/dist_ivt_low')

    # ax0 = axs[0]
    # ax0.set_xscale('linear')
    # plt.show()

    pgw = PGW(filename='ivt_1000_700.nc', rename=True, val_min=100, val_max=1000,
                            unit=r"Low-Level Integrated Vapor Transport (kg m s$^{-1}$)",
                            var_name='ivt', time_start="2025-11-25", time_end="2025-11-26",
                            time_stat=None, ens_stat='mean')
    pgw.plot_dist_change(change_val_min=10, change_val_max=1_000, pct=0.90,
                             change_min=-10, change_max=15, outfile=r'./figs/compare/finals/dist_ivt')
