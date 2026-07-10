import geopandas as gpd
import h3
from shapely.geometry import Polygon

# Load boundary
mumbai = gpd.read_file("data/mumbai_boundary.geojson")

boundary = mumbai.union_all()
geojson = boundary.__geo_interface__

resolution = 8

hex_ids = list(h3.geo_to_cells(geojson, resolution))

polygons = []

for h in hex_ids:
    boundary = h3.cell_to_boundary(h)

    # H3 returns (lat, lon)
    polygon = Polygon([(lon, lat) for lat, lon in boundary])

    polygons.append({
        "hex_id": h,
        "geometry": polygon
    })

hex_gdf = gpd.GeoDataFrame(polygons, crs="EPSG:4326")

print(hex_gdf.head())
print(len(hex_gdf))

hex_gdf.to_file(
    "data/mumbai_hexagons.geojson",
    driver="GeoJSON"
)

""" import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10,10))

hex_gdf.boundary.plot(ax=ax)

plt.show() """