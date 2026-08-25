import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

# Plot settings
font_size = 8
lon_min, lon_max, lat_min, lat_max = 90, 115, -5, 14

def setup(ax):
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    ax.set_xticks(np.arange(lon_min, lon_max, 4), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(lat_min, lat_max, 4), crs=ccrs.PlateCarree())
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(font_size)
   
    ax.grid(c='gray', ls='--')
    ax.coastlines(linewidth=0.75)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)


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

if __name__ == '__main__':

    # Track file
    trackfile = './data/IBTrACS.last3years.v04r01.nc'
    df = load_best_track_data(trackfile)

    # ERA5 file
    ncfile = "./data/sat/MSWEP/daily/daily.nc"

    # Defined event box
    event_lon_min, event_lon_max = 90, 115
    event_lat_min, event_lat_max = -5, 14

    # Plotting extent
    plot_lon_min, plot_lon_max = 90, 115
    plot_lat_min, plot_lat_max = -5, 14

    # Time range
    time_start = "2025-11-25"
    time_end   = "2025-11-28"

    # Read data
    ds = xr.open_dataset(ncfile)
    tp = ds["precipitation"]
    tp_sel = tp.sel(time=slice(time_start, time_end))

    # Accumulated precipitation (mm)
    tp_acc = tp_sel.sum(dim="time")
    levels = np.linspace(100, 500, 10)

    # Set up plot
    fig = plt.figure(figsize=(7,7))
    ax = plt.axes(projection=ccrs.PlateCarree())
    setup(ax)

    # Add precipitation
    cf = ax.contourf(tp_acc.lon, tp_acc.lat, tp_acc, cmap="Blues",
                    extend='both', levels=levels, 
                    shading="auto", transform=ccrs.PlateCarree())

    # CYCLONE TRACK
    ax.plot(df['lon'], df['lat'], color='tab:red', label='cyclone track')

    # EVENT BOX
    ax.plot([event_lon_min, event_lon_max, event_lon_max, event_lon_min, event_lon_min],
        [event_lat_min, event_lat_min, event_lat_max, event_lat_max, event_lat_min],
        color="red", linewidth=2.5, label="defined event", transform=ccrs.PlateCarree(), zorder=5)

    # Legend
    ax.legend(loc='lower left')

    # Gridlines
    gl = ax.gridlines(draw_labels=True, linestyle="--", alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False

    # Colorbar
    cbar = plt.colorbar(cf, ax=ax, pad=0.01, fraction=0.03)
    cbar.set_label("25-28Nov2025 Accumulated rainfall (mm)", fontsize=font_size, fontweight='bold')
    cbar.ax.tick_params(labelsize=font_size)

    # Final
    plt.tight_layout()
    plt.savefig('./figs/event_sat.png')