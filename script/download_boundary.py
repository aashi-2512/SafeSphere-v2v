import geopandas as gpd

gdf = gpd.read_file("data/gadm41_IND.gpkg", layer="ADM_ADM_2")

mumbai = gdf[
    gdf["NAME_2"].isin(["Mumbai City", "Mumbai Suburban"])
]

print(mumbai)

mumbai_boundary = mumbai.dissolve()

print(mumbai_boundary)

import matplotlib.pyplot as plt

mumbai_boundary.plot(figsize=(8,8))
plt.show()

mumbai_boundary.to_file(
    "data/mumbai_boundary.geojson",
    driver="GeoJSON"
)