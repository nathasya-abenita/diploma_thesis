from mod_pgw import SpatialMap

if __name__ == '__main__':
    # Create spatial map
    mapTool = SpatialMap(filename='ttenlsc_max.nc', val_min=0.01, val_max=0.05,
                         unit=r"Maximum Diabatic Heating (K s$^{-1}$)",
                         var_name='ttenlsc', time_start="2025-11-25", time_end="2025-11-26",
                         time_stat='max', ens_stat='max')

    mapTool.plot_map(r'./figs/compare/finals/map_diab.png')

    # Create distribution change graph