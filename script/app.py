import geopandas as gpd
import joblib
from geopy.geocoders import Nominatim
from shapely.geometry import Point

# Load dataset
gdf = gpd.read_file("data/mumbai_ml_dataset.geojson")

# Load trained model
model = joblib.load("model.pkl")

print("Dataset loaded successfully!")
print("Model loaded successfully!")

# Initialize geocoder
geolocator = Nominatim(user_agent="mumbai_women_safety")

# Ask user for a location
location_name = input("Enter a location in Mumbai: ")

# Geocode the location
location = geolocator.geocode(location_name)

if location is None:
    print("Location not found.")
    exit()

latitude = location.latitude
longitude = location.longitude

print(f"\nLatitude : {latitude}")
print(f"Longitude: {longitude}")

# Create a Point object
point = Point(longitude, latitude)

# Find the hexagon that contains the point
matched = gdf[gdf.contains(point)]

if matched.empty:
    print("The location is outside the Mumbai boundary.")
    exit()

# Get the matching row
row = matched.iloc[0]

print("\nHexagon Found!")
print("Hex ID:", row["hex_id"])

# Create feature vector in the same order used during training
features = [[
    row["police_distance"],
    row["hospital_distance"],
    row["railway_distance"],
    row["metro_distance"],
    row["bus_stop_distance"],
    row["restaurants"],
    row["parks"],
    row["schools"],
    row["pharmacies"],
    row["crime_count"],
]]

# Predict safety score
predicted_score = model.predict(features)[0]

print("\n" + "=" * 40)
print("      Women's Safety Score")
print("=" * 40)

print(f"\n📍 {location.address}")

print(f"\nSafety Score           : {predicted_score}/100")
print(f"Crime Count           : {row['crime_count']}")
print(f"Nearest Police Station: {row['police_distance']:.0f} m")
print(f"Nearest Hospital      : {row['hospital_distance']:.0f} m")
print(f"Nearest Railway       : {row['railway_distance']:.0f} m")
print(f"Nearest Metro         : {row['metro_distance']:.0f} m")
print(f"Nearest Bus Stop      : {row['bus_stop_distance']:.0f} m")

print(f"\nRestaurants : {row['restaurants']}")
print(f"Schools     : {row['schools']}")
print(f"Parks       : {row['parks']}")
print(f"Pharmacies  : {row['pharmacies']}")

print("=" * 40)