from track_module import CycloneTracker, load_best_track_data, font_size, plot_cyclone_tracks, plot_time_series_comparison, plot_max_sfc_wind
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def plot_case(axs, experiments, color, label, roll, nhc_data):
    track_extent = [97, 105, 2, 5]    # Used for track detection
    map_extent =[94, 107, 0, 8]
    data_dir = f"./data/final_exp"

    # Initialize tracker
    tracker = CycloneTracker(data_dir, experiments, track_extent, era5=False)
    
    # Find cyclone centers
    tracker.find_cyclone_centers(smooth_window=roll)
    
    # Compute additional variables
    tracker.compute_area_statistics('sfcWind', 'max', radius_deg=1)
    
    # Subplot (a) - Cyclone tracks 
    plot_cyclone_tracks(tracker, experiments, nhc_data=nhc_data, era5_included=False, 
                       map_extent_plot=map_extent, ax=axs[0], clean=True, color=color, label=label)
    # Add x and y labels (Longitude and Latitude)
    axs[0].set_xlabel('Longitude')
    axs[0].set_ylabel('Latitude')

    # Subplot (b) - Minimum Sea Level Pressure
    plot_time_series_comparison(tracker, 'min_pressure', experiments, nhc_data=nhc_data, ax=axs[1],
                                era5_included=False, clean=True, color=color, label=label)
    axs[1].set_title('(b)', loc='left', fontsize=font_size, fontweight='bold')
    axs[1].set_ylabel('Mean sea level pressure (hPa)', fontsize=font_size, fontweight='bold')
    
    # Subplot (c) - Maximum Wind Speed
    plot_max_sfc_wind(tracker, nhc_data=nhc_data, ax=axs[2], smooth_window=1, 
                      era5_included=False, clean=True, color=color, label=label)
    


if __name__ == '__main__':
    # Configuration
    output_path = "./figs/track/"
    roll = 0 # no roll apply to keep all timestep complete
    outfile = f"regcm_track_final_{roll}_3hr.png" # f'regcm_track_best_{roll}_new.png'

    # Load best track data
    best_track_dir = r"./data/IBTrACS.last3years.v04r01.nc"
    nhc_data = load_best_track_data(best_track_dir, time_res='3hr')

    # Create figure with 1 row and 3 columns
    plt.rcParams.update({
        "font.size": font_size,
        "axes.labelsize": font_size,
        "axes.titlesize": font_size,
        "legend.fontsize": font_size,
        "xtick.labelsize": font_size,
        "ytick.labelsize": font_size
    })

    fig = plt.figure(figsize=(14, 4))
    axs = [fig.add_subplot(1, 3, 1, projection=ccrs.PlateCarree()),
           fig.add_subplot(1, 3, 2),
           fig.add_subplot(1, 3, 3)]

    # Scenario: past
    gwl_path = 'GWL-1.5'
    experiments = [ f'counterfactual/{gwl_path}/tweak', 
                    f'counterfactual/{gwl_path}/EC-Earth3-Veg', 
                    f'counterfactual/{gwl_path}/MPI-ESM1-2-HR', 
                    f'counterfactual/{gwl_path}/NorESM2-MM']
    plot_case(axs, experiments, color='tab:blue', label='past -1.5K', roll=roll, nhc_data=nhc_data)

    # Scenario: present
    experiments = ['factual']
    plot_case(axs, experiments, color='k', label='present', roll=roll, nhc_data=None)

    # Scenario: past
    gwl_path = 'GWL+1.5'
    experiments = [ f'counterfactual/{gwl_path}/tweak', 
                    f'counterfactual/{gwl_path}/EC-Earth3-Veg', 
                    f'counterfactual/{gwl_path}/MPI-ESM1-2-HR', 
                    f'counterfactual/{gwl_path}/NorESM2-MM']
    plot_case(axs, experiments, color='tab:red', label='fut. +1.5K', roll=roll, nhc_data=None)

    plt.tight_layout()
    plt.savefig(output_path + outfile, dpi=400, bbox_inches='tight')
    plt.show()

