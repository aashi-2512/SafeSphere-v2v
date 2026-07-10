import geopandas as gpd
import pandas as pd

# Model training script
def add_nearest_distance(
    hexagon_file,
    feature_file,
    output_column,
    output_file=None
):
    """
    Adds the distance from each hexagon centroid to the nearest feature.

    Parameters
    ----------
    hexagon_file : str
        Path to the hexagon GeoJSON.

    feature_file : str
        Path to the feature GeoJSON (police, hospital, etc.).

    output_column : str
        Name of the distance column to create.

    output_file : str, optional
        Output GeoJSON path.
    """

    # ----------------------------
    # Load data
    # ----------------------------

    hexagons = gpd.read_file(hexagon_file)
    features = gpd.read_file(feature_file)

    print(f"\nAdding {output_column}...")
    print(f"Loaded {len(hexagons)} hexagons")
    print(f"Loaded {len(features)} features")

    # ----------------------------
    # Convert to projected CRS (meters)
    # ----------------------------

    hexagons = hexagons.to_crs(epsg=32643)
    features = features.to_crs(epsg=32643)

    # ----------------------------
    # Convert feature geometries to points
    # (safe even if they are already points)
    # ----------------------------

    features["geometry"] = features.geometry.centroid

    # ----------------------------
    # Create temporary centroid GeoDataFrame
    # ----------------------------

    centroids = hexagons.copy()
    centroids = centroids.set_geometry(
        centroids.geometry.centroid
    )

    # ----------------------------
    # Find nearest feature
    # ----------------------------

    nearest = gpd.sjoin_nearest(
        centroids,
        features[["geometry"]],
        how="left",
        distance_col=output_column
    )

    # ----------------------------
    # Add distance column
    # ----------------------------

    hexagons[output_column] = nearest[output_column].values

    # ----------------------------
    # Convert back to WGS84
    # ----------------------------

    hexagons = hexagons.to_crs(epsg=4326)

    # ----------------------------
    # Save
    # ----------------------------

    if output_file is None:
        output_file = hexagon_file

    hexagons.to_file(output_file, driver="GeoJSON")

    print(f"✓ {output_column} added successfully.")

def add_count_inside_hexagon(
    hexagon_file,
    feature_file,
    output_column,
    output_file=None
):
    """
    Counts how many features fall inside each hexagon.

    Parameters
    ----------
    hexagon_file : str
        Path to the hexagon GeoJSON.

    feature_file : str
        Path to the feature GeoJSON (restaurants, parks, schools, etc.)

    output_column : str
        Name of the count column to create.

    output_file : str, optional
        Output GeoJSON path.
    """

    import geopandas as gpd

    # ----------------------------
    # Load data
    # ----------------------------

    hexagons = gpd.read_file(hexagon_file)
    features = gpd.read_file(feature_file)

    print(f"\nAdding {output_column}...")
    print(f"Loaded {len(hexagons)} hexagons")
    print(f"Loaded {len(features)} features")

    # ----------------------------
    # Ensure same CRS
    # ----------------------------

    hexagons = hexagons.to_crs(epsg=4326)
    features = features.to_crs(epsg=4326)

    # ----------------------------
    # Spatial Join
    # ----------------------------

    joined = gpd.sjoin(
        features,
        hexagons,
        how="left",
        predicate="within"
    )

    # ----------------------------
    # Count features per hexagon
    # ----------------------------

    counts = joined.groupby("hex_id").size()

    # ----------------------------
    # Add count column
    # ----------------------------

    hexagons[output_column] = (
        hexagons["hex_id"]
        .map(counts)
        .fillna(0)
        .astype(int)
    )

    # ----------------------------
    # Save
    # ----------------------------

    if output_file is None:
        output_file = hexagon_file

    hexagons.to_file(output_file, driver="GeoJSON")

    print(f"✓ {output_column} added successfully.")

def add_crime_count(
    hexagon_file,
    crime_file,
    output_column,
    output_file=None
):
    """
    Counts crime incidents inside each hexagon from an Excel file.
    """

    # ----------------------------
    # Load data
    # ----------------------------

    hexagons = gpd.read_file(hexagon_file)
    crime = pd.read_excel(crime_file)

    print(f"\nAdding {output_column}...")
    print(f"Loaded {len(hexagons)} hexagons")
    print(f"Loaded {len(crime)} crime records")

    # ----------------------------
    # Convert crime table to GeoDataFrame
    # ----------------------------

    crime = gpd.GeoDataFrame(
        crime,
        geometry=gpd.points_from_xy(
            crime["long"],
            crime["lat"]
        ),
        crs="EPSG:4326"
    )

    # ----------------------------
    # Spatial Join
    # ----------------------------

    joined = gpd.sjoin(
        crime,
        hexagons,
        how="left",
        predicate="within"
    )

    # ----------------------------
    # Count crimes per hexagon
    # ----------------------------

    counts = joined.groupby("hex_id").size()

    # ----------------------------
    # Add column
    # ----------------------------

    hexagons[output_column] = (
        hexagons["hex_id"]
        .map(counts)
        .fillna(0)
        .astype(int)
    )

    # ----------------------------
    # Save
    # ----------------------------

    if output_file is None:
        output_file = hexagon_file

    hexagons.to_file(output_file, driver="GeoJSON")

    print(f"✓ {output_column} added successfully.")