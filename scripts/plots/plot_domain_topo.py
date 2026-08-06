import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

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

# Create figure with 1 row and 3 columns
font_size = 12
plt.rcParams.update({
    "font.size": font_size,
    "axes.labelsize": font_size,
    "axes.titlesize": font_size,
    "legend.fontsize": font_size,
    "xtick.labelsize": font_size,
    "ytick.labelsize": font_size
})

#%% USER INPUT

# Track file
trackfile = './data/IBTrACS.last3years.v04r01.nc'
df = load_best_track_data(trackfile)

# Topo file
ncfile = "./data/GMTED2010_15n015_0050deg.nc"

# Defined event box
event_lon_min, event_lon_max = 80, 120
event_lat_min, event_lat_max = -26, 14

# Plotting extent
plot_lon_min, plot_lon_max = 80, 120
plot_lat_min, plot_lat_max = -26, 14


#%% OPEN DATA

ds = xr.open_dataset(ncfile)
elev = ds['elevation']

#%% PLOT

fig = plt.figure(figsize=(7,7))
ax = plt.axes(projection=ccrs.PlateCarree())

# Plot extent
ax.set_extent([plot_lon_min, plot_lon_max, plot_lat_min, plot_lat_max], crs=ccrs.PlateCarree())

# Elevation

pcm = ax.pcolormesh(elev.longitude, elev.latitude, elev, cmap="terrain", shading="auto", vmin=0, vmax=1000,
    transform=ccrs.PlateCarree(), zorder=1)

# Land + coastlines
ax.add_feature(cfeature.LAND, facecolor="none", edgecolor="none", zorder=3)
ax.add_feature(cfeature.COASTLINE, linewidth=1, zorder=4)
ax.add_feature(cfeature.BORDERS, linestyle=":", zorder=4)

# CYCLONE TRACK
ax.plot(df['lon'], df['lat'], color='tab:red', label='TC track')

# Legend
ax.legend(loc='lower left')

# Gridlines
gl = ax.gridlines(draw_labels=True, linestyle="--", alpha=0.5)
gl.top_labels = False
gl.right_labels = False

# Colorbar
cbar = plt.colorbar(pcm,ax=ax, pad=0.08, fraction=0.06, aspect=40, orientation="horizontal",)
cbar.set_label("Elevation (m)")
plt.tight_layout()
plt.savefig('./figs/domain_elev.png')