from mod_pgw import PGW
import numpy as np

if __name__ == '__main__':
    mod_pr = lambda da : da * 3_600 # mm / s to mm / hr

    #%% Focus on Aceh

    # Create spatial map
    pgw = PGW(filename='pr_SRF.nc', val_min=0, val_max=570, val_modify_func=mod_pr, 
                        unit=r"Accumulated precipitation 25-26Nov2025 (mm)",
                        var_name='pr', time_start="2025-11-25", time_end="2025-11-26",
                        time_stat='sum', ens_stat='mean')
#     pgw.plot_map(outfile=r'./figs/compare/finals/map_pr_mean_with_impact.png', 
#                  polygon_path='./data/shp/Aceh.geojson',
#                  add_impact_markers=True)

    # Create distribution change graph
    pgw = PGW(filename='pr_SRF.nc', val_min=0, val_max=120, val_modify_func=mod_pr, path_mask='data/shp/mask_aceh.nc',
            unit=r'Precipitation (mm h$^{-1}$)',
            var_name='pr', time_start="2025-11-25", time_end="2025-11-26",
            time_stat=None, ens_stat='mean')
    
    pgw.plot_dist_change(change_val_min=5, change_val_max=90, add_cc_limit=True, pct=0.99, bins=np.arange(0, 120, 1),
                         change_min=-10, change_max=30, outfile=r'./figs/compare/finals/dist_pr_mean')

    #%% Focus on All Affected Provinces

    # Create spatial map
    # pgw = PGW(filename='pr_SRF.nc', val_min=0, val_max=570, val_modify_func=mod_pr, 
    #                     unit=r"Accumulated precipitation 25-26Nov2025 (mm)",
    #                     var_name='pr', time_start="2025-11-25", time_end="2025-11-26",
    #                     time_stat='sum', ens_stat='mean')
    # pgw.plot_map(outfile=r'./figs/compare/finals/map_pr_mean_with_impact_all.png', 
    #                 polygon_path='./data/shp/Sumatra_Affected_Provinces.geojson',
    #                 add_impact_markers=True)

    # # Create distribution change graph
    # pgw = PGW(filename='pr_SRF.nc', val_min=0, val_max=6, val_modify_func=mod_pr, path_mask='data/shp/mask_sumatra.nc',
    #         unit=r'Precipitation (mm h$^{-1}$)',
    #         var_name='pr', time_start="2025-11-25", time_end="2025-11-26",
    #         time_stat=None, ens_stat='mean')
    
    # pgw.plot_dist_change(change_val_min=5, change_val_max=90, add_cc_limit=True,
    #                         change_min=-10, change_max=30, outfile=r'./figs/compare/finals/dist_pr_mean_all')