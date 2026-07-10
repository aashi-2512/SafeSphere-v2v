import geopandas as gpd

gdf = gpd.read_file("data/mumbai_features.geojson")

print(gdf.columns)

print("\nFirst 5 rows:")
print(gdf.head())

print("\nDistance statistics:")
print(
    gdf[
        [
            "police_distance",
            "hospital_distance",
            "railway_distance",
            "metro_distance",
            "bus_stop_distance"
        ]
    ].describe()
)