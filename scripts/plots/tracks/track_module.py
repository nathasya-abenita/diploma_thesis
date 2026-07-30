import os
import glob
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

domain = 'large'
font_size = 10

COLORS = ["#33a02c", "#005B72","#905dc7", "#692510","#fdbf6f", "b", "#fb9a99", "#b2df8a",  "#a6cee3", "#ff7f00",  "#cab2d6"]

# CYCLONE CENTER DETECTION
def haversine_distance(lat1, lon1, lat2, lon2):
    """Compute great-circle distance (km) between two lat/lon points."""
    R = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))


class CycloneTracker:
    """
    Class to track cyclone centers and compute associated meteorological variables.
    """
    
    def __init__(self, data_dir, experiments, map_extent, era5=True):
        """
        Initialize the cyclone tracker.
        
        Parameters:
        -----------
        filepath : str
            Base path to data files
        experiments : list
            List of experiment names
        map_extent : list
            [lon_min, lon_max, lat_min, lat_max] for analysis domain
        """
        self.data_dir = data_dir
        self.experiments = experiments
        self.map_extent = map_extent
        self.cyclone_centers = {}
        self.minimum_datetime = {}
        self.variable_data = {}
        
        # Load model datasets
        self.ds_models = {}
        for exp in experiments:
            try:
                self.ds_models[exp] = load_regcm5_multi_file(os.path.join(data_dir, exp))
            except FileNotFoundError:
                print(f"Warning: Could not load data for experiment {exp}")
        
        # Load ERA5 data
        if era5:
            try:
                era_dir = "./data/era5"
                self.ds_era = load_era5(era_dir)
                self.ds_era = self.ds_era.rename({
                "valid_time": "time",
                "latitude": "lat",
                "longitude": "lon",
                "pressure_level": "plev",
                "msl": "psl",
                "t": "ta",
                "u10": "uas",
                "u": "ua",
                "v10": "vas",
                "v": "va"
                # "w": "wa"
                })
                self.ds_era = self.fix_longitude(self.ds_era, 'lon')

                # Add sfcWind
                self.ds_era['sfcWind'] = (self.ds_era['uas'] ** 2 + self.ds_era['vas']) ** 0.5

                # Save to models list
                self.ds_models["ERA5"] = self.ds_era
                
            except FileNotFoundError:
                print("Warning: Could not load ERA5 data")
                self.ds_era = None

    def fix_longitude(self, ds, lon_var):
        """Fix longitude range to [-180, 180] if necessary."""
        if np.any(ds[lon_var] > 180):
            ds.coords[lon_var] = (ds.coords[lon_var] + 180) % 360 - 180
            ds = ds.sortby(ds[lon_var])
        return ds
    
    def find_cyclone_centers(self, psl_threshold=1010.0, max_jump_km=600, smooth_window=None):
        """
        Find cyclone centers based on minimum sea level pressure,
        with robustness checks for dissipation and spurious jumps.
        
        Parameters
        ----------
        psl_threshold : float
            Minimum central pressure (hPa) to be considered a cyclone.
        max_jump_km : float
            Maximum allowed displacement per timestep (km).
        smooth_window : int or None
            Rolling window size for smoothing (timesteps). None disables smoothing.
        """
        print("Finding cyclone centers...")

        def process_dataset(ds, lat_name, lon_name, time_name, exp_name, max_jump_km):
            centers = []
            last_lat, last_lon = None, None

            for time_val in ds[time_name].values:
                ds_sel = ds.where(
                                 (ds.lat >= min(self.map_extent[2], self.map_extent[3])) &
                                 (ds.lat <= max(self.map_extent[2], self.map_extent[3])) &
                                 (ds.lon >= self.map_extent[0]) &
                                 (ds.lon <= self.map_extent[1]) &
                                 (ds.time == time_val),
                                 drop=True
                            )

                # Pressure in hPa
                pressure = ds_sel['psl']
                if pressure.attrs.get('units', '').lower() == 'pa':
                    pressure = pressure / 100.0
                
                if np.all(np.isnan(pressure.values)):
                    continue

                # Find min pressure
                min_pressure = pressure.min().item()
                min_point = pressure.where(pressure == min_pressure, drop=True)
                lat_center = min_point[lat_name].values.flatten()[0]
                lon_center = min_point[lon_name].values.flatten()[0]

                # Filters
                valid = True
                if min_pressure > psl_threshold:
                    valid = False
                if valid and last_lat is not None:
                    dist = haversine_distance(last_lat, last_lon, lat_center, lon_center)
        
                    if dist > max_jump_km:
                        valid = False

                if not valid:
                
                    lat_center, lon_center, min_pressure = np.nan, np.nan, np.nan

                centers.append({
                    'time': pd.to_datetime(time_val),
                    'lat': lat_center,
                    'lon': lon_center,
                    'min_pressure': min_pressure,
                    'experiment': exp_name
                })

                if valid:
                    last_lat, last_lon = lat_center, lon_center

            df = pd.DataFrame(centers)

            # Optional smoothing 
            if smooth_window is not None and smooth_window > 1:
                df['lat'] = df['lat'].rolling(window=smooth_window, min_periods=1, center=True).mean()
                df['lon'] = df['lon'].rolling(window=smooth_window, min_periods=1, center=True).mean()
                df['min_pressure'] = df['min_pressure'].rolling(window=smooth_window, min_periods=1, center=True).mean()

            return df

        # Process models
        for exp_name, ds in self.ds_models.items():
            print(f"Processing experiment: {exp_name}")
            ds = self.fix_longitude(ds, 'lon')
            centers = process_dataset(ds, 'lat', 'lon', 'time', exp_name, max_jump_km=max_jump_km)
            self.cyclone_centers[exp_name] = centers
            self.minimum_datetime[exp_name] = centers.iloc[centers["min_pressure"].idxmin()]
            
            # Print ERA5 tracking information
            if exp_name == "ERA5":
                print("\n" + "="*60)
                print("ERA5 CYCLONE TRACKING INFORMATION")
                print("="*60)
                print(f"\nNumber of tracked positions: {len(centers.dropna())}")
                print(f"\nMinimum pressure: {centers['min_pressure'].min():.1f} hPa at {centers.loc[centers['min_pressure'].idxmin(), 'time']}")
                print(f"  Latitude: {centers.loc[centers['min_pressure'].idxmin(), 'lat']:.2f}°")
                print(f"  Longitude: {centers.loc[centers['min_pressure'].idxmin(), 'lon']:.2f}°")
                
                print("\nTrack details (time, lat, lon, pressure):")
                print("-"*60)
                for idx, row in centers.dropna().iterrows():
                    print(f"{row['time'].strftime('%Y-%m-%d %H:%M')} | Lat: {row['lat']:6.2f} | Lon: {row['lon']:7.2f} | Pressure: {row['min_pressure']:6.1f} hPa")
                print("="*60 + "\n")

    
    def compute_area_statistics(self, var_name, stat_type='max', radius_deg=2.0):
        """
        Compute statistics for a variable in an area around the cyclone center.
        
        Parameters:
        -----------
        var_name : str
            Variable name ('sfcWind', 'pr', 'tas', 'psl')
        stat_type : str
            Type of statistic ('max', 'mean', 'min')
        radius_deg : float
            Radius around center in degrees
        """
        print(f"Computing {stat_type} {var_name} around cyclone centers...")
        models = self.ds_models
        for exp_name, ds in models.items():
            if exp_name not in self.cyclone_centers:
                results.append({
                        'time': center['time'],
                        'lat': center['lat'],
                        'lon': center['lon'],
                        f'{stat_type}_{var_name}': stat_value,
                        'experiment': exp_name
                    })
            else:
                centers_df = self.cyclone_centers[exp_name]
                results = []
                
                for _, center in centers_df.iterrows():
                    if center.isna().any():
                        # continue
                        results.append({
                                'time': center['time'],
                                'lat': center['lat'],
                                'lon': center['lon'],
                                f'{stat_type}_{var_name}': np.nan,
                                'experiment': exp_name
                            })
                    else:
                        # Define area around center
                        lat_min = center['lat'] - radius_deg
                        lat_max = center['lat'] + radius_deg
                        lon_min = center['lon'] - radius_deg
                        lon_max = center['lon'] + radius_deg
                        
                        # Select data around center
                        try:
                            ds_area = ds.where(
                                        (ds.lat >= min(lat_min, lat_max)) &
                                        (ds.lat <= max(lat_min, lat_max)) &
                                        (ds.lon >= lon_min) &
                                        (ds.lon <= lon_max) &
                                        (ds.time == center['time']),
                                        drop=True
                                    )
                            
                            var_data = ds_area[var_name]
                            
                            # Compute statistic
                            if stat_type == 'max':
                                stat_value = var_data.max().item()
                            elif stat_type == 'mean':
                                stat_value = var_data.mean().item()
                            elif stat_type == 'min':
                                stat_value = var_data.min().item()
                            else:
                                raise ValueError(f"Unknown stat_type: {stat_type}")
                            

                            results.append({
                                'time': center['time'],
                                'lat': center['lat'],
                                'lon': center['lon'],
                                f'{stat_type}_{var_name}': stat_value,
                                'experiment': exp_name
                            })
                            
                        except Exception as e:
                            print(f"Warning: Could not compute {var_name} for {exp_name} at {center['time']}: {e}")
                            continue
                    
            # Store results
            key = f"{exp_name}-{stat_type}-{var_name}"
            self.variable_data[key] = pd.DataFrame(results)


# PLOTTING FUNCTIONS  
def plot_time_series_comparison(tracker, var_name, experiments=None, nhc_data=None, 
                               era5_included=True, ax=None, clean=False, color=None, label=None, **kwargs):
    """
    Plot time series comparison of a variable across experiments.
    """
    
    if ax is None:
        fig, ax = plt.subplots()
    
    if experiments is None:
        experiments = list(tracker.cyclone_centers.keys())
        if not era5_included and 'ERA5' in experiments:
            experiments.remove('ERA5')
    
    # Plot model experiments
    if not clean:
        for i, exp in enumerate(experiments):
            if exp == 'ERA5':
                continue
                
            if exp in tracker.cyclone_centers:
                df = tracker.cyclone_centers[exp]
                
                if var_name in df.columns:
                    color = COLORS[i % len(COLORS)]
                    ax.plot(df['time'], df[var_name], 'o-', 
                        label=exp, color=color, alpha=0.8, **kwargs)
    else:
        # Collect wind speed time series
        wind_list = []
        for exp in experiments:
            df = tracker.cyclone_centers[exp]
            wind_list.append(df[var_name].values)
        # Compute ensemble stats
        ens_wind_mean, ens_wind_std = compute_ens_stat_std(wind_list, stat='mean')
        # Plot ensemble mean
        ax.plot(df['time'], ens_wind_mean, 'o-', 
                label=label, color=color, alpha=1, **kwargs)
        # Plot ensemble spread
        ax.fill_between(df['time'], ens_wind_mean - ens_wind_std, ens_wind_mean + ens_wind_std, 
                color=color, alpha=0.25, edgecolor=None, **kwargs)
        
    # Plot ERA5 if requested
    if era5_included and 'ERA5' in tracker.cyclone_centers:
        df_era5 = tracker.cyclone_centers['ERA5']
        df_era5 = df_era5.drop(index=range(23, 28), errors="ignore")
        if var_name in df_era5.columns:
            ax.plot(df_era5['time'], df_era5[var_name], 'o-', 
                   label='ERA5', color='blue', alpha=0.8)
    
    # Plot NHC data if provided
    if nhc_data is not None and var_name in nhc_data.columns:
        ax.plot(nhc_data['time'], nhc_data[var_name], 'o-', 
               label='IBTrACS', color="tab:orange", linewidth=2)
    
    ax.set_ylabel(var_name)
    ax.legend()
    ax.grid(True, linestyle='--')
    ax.tick_params(axis='x', rotation=45)
    
    return ax

def compute_ens_stat_std (val_list, stat):
    stacked_val = np.stack(val_list)
    if stat == 'mean':
        ens_val = np.nanmean(stacked_val, axis=0) 
        ens_val_std  = np.nanstd(stacked_val, axis=0)
    elif stat == 'median':
        ens_val = np.nanmedian(stacked_val, axis=0) 
        ens_val_std  = np.nanstd(stacked_val, axis=0)
    else:
        raise ValueError ('check stat option!')
    return ens_val, ens_val_std 

def plot_cyclone_tracks(tracker, experiments=None, nhc_data=None, era5_included=True, 
                        map_extent_plot=None, ax=None, clean=False, color=None, label=None):
    """
    Plot cyclone tracks on a map.
    
    Parameters:
    -----------
    map_extent_plot : list or None
        [lon_min, lon_max, lat_min, lat_max] for map extent in the plot.
        If None, uses tracker.map_extent.
    clean : boolean
        if True, experiments are plotted as 6-hourly values with ensemble mean and spread.
        Otherwise, the raw hourly statistics are plotted.
    """
    
    if ax is None:
        fig = plt.figure()
        ax = plt.axes(projection=ccrs.PlateCarree())
    
    # Use plot-specific map extent or fall back to tracker's map_extent
    plot_extent = map_extent_plot if map_extent_plot is not None else tracker.map_extent
    
    # Base map
    ax.add_feature(cfeature.COASTLINE, linewidth=0.75)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle=":")
    ax.add_feature(cfeature.LAND, facecolor="lightgray")
    ax.add_feature(cfeature.OCEAN, facecolor="lightblue")
    ax.set_extent(plot_extent, crs=ccrs.PlateCarree())
    
    if experiments is None:
        experiments = [exp for exp in tracker.cyclone_centers.keys() if exp != 'ERA5']
    
    # Plot model tracks
    if not clean:
        for i, exp in enumerate(experiments):
            if exp in tracker.cyclone_centers:
                df = tracker.cyclone_centers[exp]
                color = COLORS[i % len(COLORS)]
                
                # Plot track
                ax.plot(df['lon'], df['lat'], 'o-', color=color, 
                    linewidth=1, markersize=4, label=exp, alpha=0.8)
                
                # Mark start point
                ax.scatter(df['lon'].iloc[0], df['lat'].iloc[0], 
                        marker='*', s=75, color=color, 
                        edgecolor='black', zorder=5)
    else:
        # Prepare list to save values
        lon_list, lat_list = [], [] # each item is time series for an experiment

        # Compute ensemble mean and spread
        for exp in experiments:
            df = tracker.cyclone_centers[exp]
            lon_list.append(df['lon'].values[::6])
            lat_list.append(df['lat'].values[::6])
            ax.plot(df['lon'], df['lat'], '-', color=color, linewidth=1, alpha=0.2)
        ens_lon_mean, ens_lon_std = compute_ens_stat_std(lon_list, stat='median')
        ens_lat_mean, ens_lat_std = compute_ens_stat_std(lat_list, stat='median')

        # Plot
        # Plot track
        ax.plot(ens_lon_mean, ens_lat_mean, 'o-', color=color, 
            linewidth=1, markersize=4, label=label, alpha=0.8)
        
        # Mark start point
        ax.scatter(df['lon'].iloc[0], df['lat'].iloc[0], 
                marker='*', s=75, color=color, zorder=5, edgecolor='k')

    # Plot ERA5 track
    if era5_included and 'ERA5' in tracker.cyclone_centers:
        df_era5 = tracker.cyclone_centers['ERA5']
        print(df_era5)
        ax.plot(df_era5['lon'], df_era5['lat'], 's-', color='blue',
               linewidth=1, markersize=3, label='ERA5', alpha=0.8)
        ax.scatter(df_era5['lon'].iloc[0], df_era5['lat'].iloc[0],
                  marker='*', s=75, color='blue', edgecolor='black', zorder=5)
    
    # Plot best track
    if nhc_data is not None:
        print(nhc_data)
        ax.plot(nhc_data['lon'], nhc_data['lat'], 's-', color="tab:orange",
               linewidth=1, markersize=3, label='IBTrACS', alpha=0.8)
        ax.scatter(nhc_data['lon'].iloc[0], nhc_data['lat'].iloc[0],
                  marker='*', s=75, color="r", edgecolor='black', zorder=5)
    
    # Add x and y labels (Longitude and Latitude)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    
    # Formatting with longitude/latitude formatters
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    
    # Add gridlines with labels
    gl = ax.gridlines(draw_labels=True, linestyle='--', 
                     xlocs=range(95, 110, 2), 
                     ylocs=range(0, 8, 2))
    gl.top_labels = False
    gl.right_labels = False

    # ax.legend(loc=3, fontsize=font_size)
    ax.set_title('(a)', loc='left', fontsize=font_size, fontweight='bold')
    ax.legend()
    return ax

def plot_max_sfc_wind(tracker, nhc_data=None, ax=None, smooth_window=1, era5_included=True,
                      clean=False, label=None, color=None):
    """Plot maximum surface wind speed."""
    if ax is None:
        fig, ax = plt.subplots()

    if not clean:
        # Plot model experiments
        for i, var in enumerate(tracker.variable_data.keys()):
            if (var == 'ERA5') and (era5_included == False):
                continue
            else:
                expname = var.split("-")[0]
                moist_data = tracker.variable_data[var]
                moist_data['max_sfcWind'] = moist_data['max_sfcWind'].rolling(window=smooth_window, min_periods=1, center=True).mean()
                color = COLORS[i] if ('ERA5' not in var) else 'blue'
                ax.plot(moist_data['time'], moist_data['max_sfcWind'], 
                        'o-', label=expname, alpha=0.8, color=color)
    else:
        # Collect wind speed time series
        wind_list = []
        for var in tracker.variable_data.keys():
            if (var == 'ERA5') and (era5_included == False):
                continue
            else:
                moist_data = tracker.variable_data[var]
                # moist_data['max_sfcWind'] = moist_data['max_sfcWind'].rolling(window=smooth_window, min_periods=1, center=True).mean()
                print(moist_data['max_sfcWind'].shape)
                wind_list.append(moist_data['max_sfcWind'].values)
        # Compute ensemble stats
        ens_wind_mean, ens_wind_std = compute_ens_stat_std(wind_list, stat='mean')
        # Plot ensemble mean
        ax.plot(moist_data['time'], ens_wind_mean, 'o-', 
                label=label, color=color, alpha=1)
        # Plot ensemble spread
        ax.fill_between(moist_data['time'], ens_wind_mean - ens_wind_std, ens_wind_mean + ens_wind_std,
                color=color, alpha=0.25, edgecolor=None)
    
    # Add NHC wind data
    if nhc_data is not None:
        ax.plot(nhc_data['time'], nhc_data['wind'] * 0.514444, 
                'o-', label='IBTrACS', color="tab:orange", linewidth=2)

    # Define bounds    
    x_min, x_max = ax.get_xlim()
    y_top = 32.7

    # Fill intervals

    intervals = [
        (0, 17.5, "lightgreen", "Tropical Depression", 1),
        (17.5, y_top, "#FFFF00", "Tropical Storm", 18.5),
    ]

    for i, (y0, y1, fill_color, label, y_text) in enumerate(intervals):
        ax.fill_between([x_min, x_max], y0, y1, color=fill_color, alpha=0.4, zorder=-10)

        # if i < len(intervals) - 1:
        #     next_y0, next_y1 = intervals[i + 1][0], intervals[i + 1][1]
        #     y_text = next_y0 - (next_y1 - next_y0)/2
        # else:
        #     y_text = y1 - (y_top - y1)/2
        if era5_included:
            x_text = pd.to_datetime(tracker.variable_data['ERA5-max-sfcWind']["time"].max()) #+ pd.Timedelta(days=-1.5)
        else:
            x_text = pd.to_datetime(moist_data['time'].min())
        ax.text(x_text, y_text, label, va='center', ha='left', fontsize=font_size, color='k')

    ax.set_ylim(0, y_top)
    ax.set_ylabel("Max wind speed (m/s)", fontsize=font_size, fontweight='bold')
    ax.set_title("(c)", loc='left', fontsize=font_size, fontweight='bold')
    ax.margins(x=0)
    ax.legend(fontsize=font_size)
    ax.tick_params(axis='x', rotation=45)
        
    return ax

def load_best_track_data(nc_file):
    """Load best track data."""

    # Read file
    ds = xr.open_dataset(nc_file)

    # Select storm, saved as DataFrame
    storm_id = 295 # Storm Senyar ID
    ds_sel = ds.sel(storm=storm_id)
    df = ds_sel[['lat', 'lon', 'usa_wind', 'usa_pres']].to_dataframe().dropna()

    # Clean DataFrame
    df = df.reset_index(drop=True)
    df['time'] = df['time'].dt.round('s')
    df = df.rename(columns={'usa_wind': 'wind', 'usa_pres': 'min_pressure'})
    return df[::2]

# Dataset loaders
def load_era5(era_dir, verbose=False):
    nc_files = sorted(glob.glob(os.path.join(era_dir, '*hr*Senyar.nc')))
    
    if not nc_files:
        raise ValueError(f"No NetCDF files found in {era_dir}")
    
    datasets = []
    for file in nc_files:
        ds_temp = xr.open_dataset(file)
        ds_temp = ds_temp.sel(valid_time=slice("2025-11-25 12:00", "2025-11-28 12:00"))
        datasets.append(ds_temp)
    
    time_coords = [set(ds.valid_time.values) for ds in datasets]
    common_times = sorted(time_coords[0].intersection(*time_coords[1:]))
    
    datasets_aligned = [ds.sel(valid_time=common_times) for ds in datasets]
    ds_merged = xr.merge(datasets_aligned, compat='override')
    
    return ds_merged

def load_regcm5_multi_file(data_dir, verbose=False):
    nc_files = sorted(glob.glob(os.path.join(data_dir, '*_SRF.nc')))
    wanted = ['psl_SRF.nc', 'sfcWind_SRF.nc']
    nc_files = [f for f in nc_files if os.path.basename(f) in wanted]

    if not nc_files:
        raise ValueError(f"No NetCDF files found in {data_dir}")

    print(nc_files)
    
    datasets = []
    for file in nc_files:
        ds_temp = xr.open_dataset(file).sel(time=slice("2025-11-25 12:00", "2025-11-28 12:00"))
        datasets.append(ds_temp)
    
    #time_coords = [set(ds.time.values) for ds in datasets]
    #common_times = sorted(time_coords[0].intersection(*time_coords[1:]))
    
    #datasets_aligned = [ds.sel(time=common_times) for ds in datasets]
    ds_merged = xr.merge(datasets, compat='override')
    
    # Rename coordinates
    ds_merged = ds_merged.rename({"xlon": "lon", "xlat": "lat"})
    return ds_merged