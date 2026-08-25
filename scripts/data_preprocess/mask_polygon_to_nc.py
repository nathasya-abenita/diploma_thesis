import geopandas as gpd
import xarray as xr
import numpy as np
from shapely.geometry import Point

# Extract polygon from geojson
gdf = gpd.read_file('./data/shp/Sumatra_Affected_Provinces.geojson')
polygon = gdf.geometry.iloc[0] 

# Read grid example
ds = xr.open_dataset("./data/final_exp_old/mask_SRF.nc")
lon = ds["xlon"] # lon[iy, jx]
lat = ds["xlat"] # lat[iy, jx]

# Update mask array
mask = np.zeros(lon.shape, dtype=bool)

for i in range(lon.shape[0]):
    for j in range(lon.shape[1]):
        mask[i, j] = polygon.contains(Point(lon[i, j], lat[i, j]))

# Finalized new NC file
ds_ = ds.copy()
ds_.mask.values = mask
ds_.to_netcdf("mask_sumatra.nc")