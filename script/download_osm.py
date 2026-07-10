import geopandas as gpd
import osmnx as ox
import os

# Load Mumbai boundary
mumbai = gpd.read_file("data/mumbai_boundary.geojson")
polygon = mumbai.union_all()

os.makedirs("data", exist_ok=True)

def download_feature(name, tags):
    print(f"\nDownloading {name}...")

    gdf = ox.features_from_polygon(
        polygon,
        tags=tags
    )

    print(f"Found {len(gdf)} features")

    gdf.to_file(f"data/{name}.geojson", driver="GeoJSON")

    print(f"Saved data/{name}.geojson")