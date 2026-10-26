from mod_pgw import PGW
import os

out_dir = "/leonardo/home/userexternal/nchristi/diploma_thesis/figs/pgw"

if __name__ == '__main__':
    # Create spatial map
    fun = lambda x : x * 1_000
    pgw = PGW(filename='evspsbl_SRF.nc', val_min=0, val_max=0.095, val_modify_func=fun,
                        unit=r"Evaporation Flux (mm s$^{-1}$)",
                        var_name='evspsbl', time_start="2025-11-25", time_end="2025-11-26",
                        time_stat='mean', ens_stat='mean')
    pgw.plot_map(outfile=os.path.join(out_dir, 'map_evs.png'))

    # Create distribution change graph
    pgw = PGW(filename='evspsbl_SRF.nc', val_min=0.02, val_max=0.2, val_modify_func=fun,
                            unit=r"Evaporation Flux (mm s$^{-1}$)",
                            var_name='evspsbl', time_start="2025-11-25", time_end="2025-11-26",
                            time_stat=None, ens_stat='mean')
    pgw.plot_dist_change(change_val_min=0.02, change_val_max=0.25, ylim_pdf=(1e-5, 1e2), pct=50,
                         change_min=-5, change_max=10, outfile=os.path.join(out_dir, 'dist_evs'))
