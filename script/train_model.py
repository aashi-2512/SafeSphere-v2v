import geopandas as gpd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

# -----------------------------
# Load Dataset
# -----------------------------
gdf = gpd.read_file("data/mumbai_ml_dataset.geojson")

# -----------------------------
# Select Features and Target
# -----------------------------
feature_columns = [
    "police_distance",
    "hospital_distance",
    "railway_distance",
    "metro_distance",
    "bus_stop_distance",
    "restaurants",
    "parks",
    "schools",
    "pharmacies",
    "crime_count",
]

X = gdf[feature_columns]
y = gdf["safety_score"]

# -----------------------------
# Train-Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
)

# -----------------------------
# Train Model
# -----------------------------
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
)

model.fit(X_train, y_train)

# -----------------------------
# Predictions
# -----------------------------
y_pred = model.predict(X_test)

# -----------------------------
# Evaluation
# -----------------------------
mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5
r2 = r2_score(y_test, y_pred)

print("\nModel Performance")
print("-" * 30)
print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R²   : {r2:.4f}")

# -----------------------------
# Feature Importance
# -----------------------------
print("\nFeature Importance")
print("-" * 30)

importance = sorted(
    zip(feature_columns, model.feature_importances_),
    key=lambda x: x[1],
    reverse=True,
)

for feature, score in importance:
    print(f"{feature:<20} {score:.4f}")

# -----------------------------
# Save Model
# -----------------------------
joblib.dump(model, "model.pkl")

print("\nModel saved as model.pkl")