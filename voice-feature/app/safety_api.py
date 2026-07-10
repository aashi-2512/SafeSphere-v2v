"""
Safety Map & Safe Route REST API for SafeSphere.

This router wraps the existing hexagonal-map + safe-route pipeline
(script/safe_route.py, model.pkl, data/) and exposes three endpoints:

    GET  /safety/score?lat=&lng=    Safety score for a GPS coordinate
    POST /safety/route              Safest + quickest walking route (GeoJSON)
    GET  /safety/hexagons           Full hexagon GeoJSON for map rendering

Data is lazy-loaded on first request and cached in module-level globals.
The safe_route module is imported dynamically via sys.path so the voice-feature
package does not need to be restructured.

Integration with SOS
────────────────────
When a user triggers POST /sos, the SOS handler can optionally call
GET /safety/score internally to attach the victim's hex safety score to the
SOS response — letting emergency contacts immediately see how dangerous the
area is without an extra round-trip from the client.
"""

import os
import sys
from fastapi import APIRouter, HTTPException, Query

from app.config import DATA_DIR, MODEL_PATH, SCRIPT_DIR
from app.logger import get_logger
from app.models import RouteRequest

logger = get_logger("safety_api")

# ── Add script/ to Python path so we can import safe_route ───────────────────
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

router = APIRouter(prefix="/safety", tags=["safety"])

# ── Module-level lazy cache ───────────────────────────────────────────────────
_gdf = None      # GeoDataFrame: hexagon dataset with features + safety scores
_model = None    # scikit-learn model loaded from model.pkl


def _get_hex_data():
    """Lazy-load the hexagon GeoDataFrame. Cached after first call."""
    global _gdf
    if _gdf is None:
        try:
            import geopandas as gpd
        except ImportError:
            raise RuntimeError("geopandas is not installed. Run: pip install geopandas")

        path = os.path.join(DATA_DIR, "mumbai_ml_dataset.geojson")
        if not os.path.exists(path):
            raise RuntimeError(
                f"Hexagon dataset not found at: {path}\n"
                f"DATA_DIR is set to: {DATA_DIR}"
            )
        _gdf = gpd.read_file(path).to_crs(epsg=4326)
        logger.info(f"Hexagon dataset loaded: {len(_gdf)} hexagons from {path}")
    return _gdf


def _get_model():
    """Lazy-load the safety score model. Cached after first call."""
    global _model
    if _model is None:
        try:
            import joblib
        except ImportError:
            raise RuntimeError("joblib is not installed. Run: pip install joblib")

        if not os.path.exists(MODEL_PATH):
            raise RuntimeError(
                f"Model file not found at: {MODEL_PATH}\n"
                f"MODEL_PATH is set to: {MODEL_PATH}"
            )
        _model = joblib.load(MODEL_PATH)
        logger.info(f"Safety score model loaded from {MODEL_PATH}")
    return _model


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/score")
def get_safety_score(
    lat: float = Query(..., description="Latitude of the location"),
    lng: float = Query(..., description="Longitude of the location"),
):
    """
    Get the predicted Women's Safety Score (0–100) for a GPS coordinate.

    Returns the score, crime statistics, and distances to key infrastructure
    for the H3 hexagon that contains the given point.

    **Higher score = safer area.**
    """
    try:
        from shapely.geometry import Point
        gdf = _get_hex_data()
        model = _get_model()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    point = Point(lng, lat)
    matched = gdf[gdf.contains(point)]

    if matched.empty:
        raise HTTPException(
            status_code=404,
            detail="The coordinates are outside the Mumbai boundary covered by this dataset.",
        )

    row = matched.iloc[0]

    feature_vector = [[
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
    predicted_score = float(model.predict(feature_vector)[0])

    return {
        "hex_id": row["hex_id"],
        "lat": lat,
        "lng": lng,
        "safety_score": round(predicted_score, 2),
        "safety_label": _score_label(predicted_score),
        "crime_count": int(row["crime_count"]),
        "nearest_police_m": round(float(row["police_distance"]), 1),
        "nearest_hospital_m": round(float(row["hospital_distance"]), 1),
        "nearest_railway_m": round(float(row["railway_distance"]), 1),
        "nearest_metro_m": round(float(row["metro_distance"]), 1),
        "nearest_bus_stop_m": round(float(row["bus_stop_distance"]), 1),
        "restaurants_in_hex": int(row["restaurants"]),
        "parks_in_hex": int(row["parks"]),
        "schools_in_hex": int(row["schools"]),
        "pharmacies_in_hex": int(row["pharmacies"]),
    }


@router.post("/route")
def get_safe_route(body: RouteRequest):
    """
    Compute the safest walking route between two locations in Mumbai.

    - **start** / **end**: Mumbai address string OR `"lat,lng"` coordinates.
    - **time_bucket**: `day` | `evening` | `night` (auto-detected from current time if omitted).

    Returns both the **safest route** (minimises crime/risk exposure) and the
    **quickest route** (shortest time), each as a list of `[lat, lng]` waypoints
    plus risk statistics.

    ⚠️ This endpoint calls the Nominatim geocoder (if address strings are used)
    which adds ~1–3 s of latency per address. Pass coordinates directly for faster results.
    """
    try:
        from safe_route import safest_route
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Safe route module could not be imported: {exc}. "
                   f"SCRIPT_DIR={SCRIPT_DIR}",
        )

    logger.info(
        f"Route request | start='{body.start}' end='{body.end}' "
        f"time_bucket={body.time_bucket}"
    )

    try:
        result = safest_route(
            body.start,
            body.end,
            time_bucket=body.time_bucket,
            data_dir=DATA_DIR,
        )
    except Exception as exc:
        logger.error(f"Route computation failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Route computation error: {exc}")

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/hexagons")
def get_hexagons():
    """
    Return the complete Mumbai hexagon GeoJSON for map rendering.

    Each feature includes:
      - `hex_id`: H3 cell identifier
      - `safety_score`: predicted score (0–100, higher = safer)
      - `safety_label`: human-readable tier (Very Safe / Safe / Moderate / Unsafe / Very Unsafe)
      - `crime_count`: crime incidents recorded in this hex

    The client can use this to render a colour-coded safety overlay
    (e.g. in Leaflet, Mapbox, or Google Maps) without querying scores per-point.
    """
    try:
        gdf = _get_hex_data()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    features = []
    for _, row in gdf.iterrows():
        score = float(row["safety_score"])
        features.append({
            "type": "Feature",
            "geometry": row.geometry.__geo_interface__,
            "properties": {
                "hex_id": row["hex_id"],
                "safety_score": round(score, 2),
                "safety_label": _score_label(score),
                "crime_count": int(row["crime_count"]),
            },
        })

    return {
        "type": "FeatureCollection",
        "features": features,
        "total_hexagons": len(features),
        "data_dir": DATA_DIR,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _score_label(score: float) -> str:
    """Convert a numeric safety score to a human-readable tier label."""
    if score >= 80:
        return "Very Safe"
    elif score >= 60:
        return "Safe"
    elif score >= 40:
        return "Moderate"
    elif score >= 20:
        return "Unsafe"
    else:
        return "Very Unsafe"
