import geopandas as gpd

gdf = gpd.read_file("data/mumbai_features.geojson")

print(gdf.columns.tolist())

gdf["safety_score"] = 100

print(gdf[["hex_id", "safety_score"]].head())
gdf["safety_score"] = gdf["safety_score"] - (gdf["crime_count"] * 8)