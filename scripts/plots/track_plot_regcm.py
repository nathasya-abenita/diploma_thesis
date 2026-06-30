from track_module import CycloneTracker, load_best_track_data, font_size, plot_cyclone_tracks, plot_time_series_comparison, plot_max_sfc_wind
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

if __name__ == "__main__":
    # Configuration
    output_path = "./figs/"

    experiments = ['factual']
    track_extent = [97, 105, 2, 5]    # Used for track detection
    map_extent =[94, 107, 0, 8]
    data_dir = f"./data/best_3km"
    best_track_dir = r"./data/IBTrACS.last3years.v04r01.nc"
    roll = 6
    
    # Initialize tracker
    tracker = CycloneTracker(data_dir, experiments, track_extent)
    
    # Find cyclone centers
    tracker.find_cyclone_centers(smooth_window=roll)
    
    # Compute additional variables
    tracker.compute_area_statistics('sfcWind', 'max', radius_deg=2)
    
    # Load best track data
    nhc_data = load_best_track_data(best_track_dir)
    
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
    
    # Subplot (a) - Cyclone tracks 
    ax1 = fig.add_subplot(1, 3, 1, projection=ccrs.PlateCarree())
    plot_cyclone_tracks(tracker, experiments, nhc_data, era5_included=True, 
                       map_extent_plot=map_extent, ax=ax1)
    # Add x and y labels (Longitude and Latitude)
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')

    # Subplot (b) - Minimum Sea Level Pressure
    ax2 = fig.add_subplot(1, 3, 2)
    plot_time_series_comparison(tracker, 'min_pressure', experiments, nhc_data, ax=ax2)
    ax2.set_title('(b)', loc='left', fontsize=font_size, fontweight='bold')
    ax2.set_ylabel('Mean sea level pressure (hPa)', fontsize=font_size, fontweight='bold')
    
    # Subplot (c) - Maximum Wind Speed
    ax3 = fig.add_subplot(1, 3, 3)
    plot_max_sfc_wind(tracker, nhc_data, ax=ax3)
    
    plt.tight_layout()
    plt.savefig(output_path + f"regcm_track_roll_{roll}.png", dpi=400, bbox_inches='tight')
    plt.show()
