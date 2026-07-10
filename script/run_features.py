from add_feature import add_nearest_distance
from add_feature import add_count_inside_hexagon
from add_feature import add_crime_count

HEX = "data/mumbai_hexagons.geojson"
OUT = "data/mumbai_features.geojson"

add_nearest_distance(
    HEX,
    "data/police.geojson",
    "police_distance",
    OUT
)

add_nearest_distance(
    OUT,
    "data/hospitals.geojson",
    "hospital_distance",
    OUT
)

add_nearest_distance(
    OUT,
    "data/railway.geojson",
    "railway_distance",
    OUT
)

add_nearest_distance(
    OUT,
    "data/metro.geojson",
    "metro_distance",
    OUT
)

add_nearest_distance(
    OUT,
    "data/bus_stops.geojson",
    "bus_stop_distance",
    OUT
)

print("\n✅ All distance features added successfully!")

add_count_inside_hexagon(
    OUT,
    "data/restaurants.geojson",
    "restaurants",
    OUT
)

add_count_inside_hexagon(
    OUT,
    "data/parks.geojson",
    "parks",
    OUT
)

add_count_inside_hexagon(
    OUT,
    "data/schools.geojson",
    "schools",
    OUT
)
add_count_inside_hexagon(
    OUT,
    "data/schools.geojson",
    "pharmacies",
    OUT
)

import geopandas as gpd

gdf = gpd.read_file("data/mumbai_features.geojson")

print(gdf[
    [
        "restaurants",
        "parks",
        "schools",
        "pharmacies"
    ]
].describe())

import pandas as pd
import geopandas as gpd




add_crime_count(
    OUT,
    "data/crime.xlsx",
    "crime_count",
    OUT
)
