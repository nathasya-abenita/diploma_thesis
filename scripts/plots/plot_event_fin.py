import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
import xarray as xr

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

# 1. Define specific coordinates from the sources
# S1: Malalak, West Sumatra (Village destroyed by flood) [2]
# S2: Bener Meriah, Aceh (Multiple shallow landslides) [2]
sites = {
    'S1': (100.278, 0.3897), # 100°16'41"E, 0°23'23"N
    'S2': (97.204, 4.665),   # 97°12'15"E, 4°39'54"N
}

# A1-A4: Remote-Sensing Sites in Aceh (Bukit Barisan mountains) [4, 5]
remote_sites = {
    'A1 (Burlah)': (96.67, 4.71),
    'A2 (Blangpanu)': (97.25, 4.68),
    'A3 (Uningmas)': (96.82, 4.86),
    'A4 (Perhutani)': (97.27, 4.61),
}

flood_hotspots = {
    'Idi Town (Aceh Timur)': (97.77, 4.95), # Approx coords
    'Lhokseumawe': (97.14, 5.18),
    'Sibolga': (98.78, 1.74),
    'Tarutung': (98.97, 2.01),
}

fig = plt.figure(figsize=(12, 8))
ax = plt.axes(projection=ccrs.PlateCarree())

# 2. Set map extent for Aceh, North Sumatra, and West Sumatra [6, 7]
ax.set_extent([94.5, 102.5, -1.5, 6.5], crs=ccrs.PlateCarree())

# 3. Add geographical features
ax.add_feature(cfeature.LAND, facecolor='lightgray')
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')
# Note: Provincial boundaries often require a GeoJSON or Shapefile



# 4. Satellite derived precipitation
ds = xr.open_dataset('./data/sat/MSWEP/daily/daily.nc')
rainfall = ds.precipitation.sel(time=slice('2025-11-25','2025-11-28')).sum(dim='time')
cf = ax.contourf(ds.lon, ds.lat, rainfall, cmap='YlGnBu')
cbar = fig.colorbar(cf, ax=ax, orientation="horizontal", pad=0.08, fraction=0.06, aspect=40)
cbar.set_label('Accumulated rainfall (mm)')

ax.add_feature(cfeature.OCEAN, facecolor="white", zorder=2) # mask ocean

# Province boundaries
province_names = ['Aceh', 'Sumatera_Utara', 'Sumatera_Barat']
province_labels = ['Aceh', 'North Sumatra', 'West Sumatra']
for name, label in zip(province_names, province_labels):
    gdf = gpd.read_file(f'./data/shp/{name}.geojson')
    gdf = gdf.to_crs(epsg=4326)
    gdf.boundary.plot(ax=ax, linestyle='--', color='k')

    # Compute a good label position
    rep_point = gdf.geometry.representative_point().iloc[0]
    x, y = rep_point.x, rep_point.y

    # Shift label upward (tweak offset as needed)
    y_offset = 0.3   # degrees; adjust depending on your map scale

    ax.text(
        x, y + y_offset, label,
        ha='center', va='bottom',
        fontsize=10, fontweight='bold',
        color='k'
    )


# 5. Plotting Disaster Points
for name, (lon, lat) in sites.items():
    ax.plot(lon, lat, 'o', color='k', markersize=6)
ax.plot([], [], 'o', color='k', label=f'Landslide Sites') # legend

# Remote Sensing Sites A1-A4
for name, (lon, lat) in remote_sites.items():
    ax.plot(lon, lat, 'o', color='k', markersize=6)

for name, (lon, lat) in flood_hotspots.items():
    ax.plot(lon, lat, 'o', color='tab:red', markersize=6)
ax.plot([], [],'o', color='tab:red', label=f'Flood Sites') # legend

# Cyclone track
df_cy = load_best_track_data('./data/IBTrACS.last3years.v04r01.nc')
ax.plot(df_cy['lon'], df_cy['lat'], '--', color='tab:red', linewidth=3, label='Cyclone track')

# 6. Final Touches
# plt.title('2025 Extreme Rainfall & Disaster Sites: Sumatra Focus', fontsize=14)
plt.legend(loc='lower left')
plt.tight_layout()
plt.savefig('./figs/event_view.png')