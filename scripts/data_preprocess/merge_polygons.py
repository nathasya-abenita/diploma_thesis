import geopandas as gpd
from shapely.ops import unary_union
import matplotlib.pyplot as plt

# Input files
files = [
    "./data/shp/Aceh.geojson",
    "./data/shp/Sumatera_Barat.geojson",
    "./data/shp/Sumatera_Utara.geojson"
]

# Read all polygons
geoms = []
for f in files:
    gdf = gpd.read_file(f)
    geoms.append(gdf.geometry.iloc[0])  

# Merge them
merged = unary_union(geoms)

# Save to GeoJSON
merged_gdf = gpd.GeoDataFrame(geometry=[merged], crs="EPSG:4326")
merged_gdf.to_file("Sumatra_Affected_Provinces.geojson", driver="GeoJSON")

# Plot for validation
fig, ax = plt.subplots()
merged_gdf.plot(ax=ax)
plt.show()
