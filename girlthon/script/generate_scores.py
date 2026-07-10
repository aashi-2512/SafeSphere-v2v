import geopandas as gpd

# ----------------------------
# Load engineered dataset
# ----------------------------

gdf = gpd.read_file("data/mumbai_features.geojson")

# ----------------------------
# Initialize Safety Score
# ----------------------------

gdf["safety_score"] = 100.0

# =====================================================
# PENALTIES
# =====================================================

# Crime (largest penalty)
gdf["safety_score"] -= gdf["crime_count"] * 8

# Distance penalties (in metres)
gdf["safety_score"] -= gdf["police_distance"] / 1000
gdf["safety_score"] -= gdf["hospital_distance"] / 2000
gdf["safety_score"] -= gdf["railway_distance"] / 3000
gdf["safety_score"] -= gdf["metro_distance"] / 4000
gdf["safety_score"] -= gdf["bus_stop_distance"] / 5000

# =====================================================
# BONUSES
# =====================================================

# More amenities generally improve accessibility
gdf["safety_score"] += gdf["parks"] * 2
gdf["safety_score"] += gdf["schools"] * 1
gdf["safety_score"] += gdf["pharmacies"] * 1
gdf["safety_score"] += gdf["restaurants"] * 0.5

# =====================================================
# Clamp score between 0 and 100
# =====================================================

gdf["safety_score"] = gdf["safety_score"].clip(0, 100)

# =====================================================
# Save final ML dataset
# =====================================================

gdf.to_file("data/mumbai_ml_dataset.geojson", driver="GeoJSON")

print("✅ Safety scores generated successfully!")

print(
    gdf[
        [
            "hex_id",
            "crime_count",
            "police_distance",
            "hospital_distance",
            "restaurants",
            "parks",
            "schools",
            "pharmacies",
            "safety_score",
        ]
    ].head(10)
)

print("\nSafety Score Statistics:")
print(gdf["safety_score"].describe())