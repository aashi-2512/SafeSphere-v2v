import pandas as pd
import geopandas as gpd
import h3
import requests
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os
import time
from enum import Enum

# --- Configuration Constants ---
H3_RES = 8
ALPHA = 0.5 # Weight for static safety score vs time risk
MAX_DETOUR_RATIO = 1.4
HIGH_RISK_THRESHOLD = 25.0
MAX_ITERATIONS = 3
TIME_BUCKETS = {
    'day': (6, 18),
    'evening': (18, 22),
    'night': (22, 6) # Handles overnight
}

class StopReason(str, Enum):
    SUCCESS = "SUCCESS"
    NO_HIGH_RISK = "NO_HIGH_RISK"
    NO_SAFER_NEIGHBOR = "NO_SAFER_NEIGHBOR"
    NO_IMPROVEMENT = "NO_IMPROVEMENT"
    MAX_DETOUR_RATIO = "MAX_DETOUR_RATIO"
    MAX_ITERATIONS = "MAX_ITERATIONS"
    OSRM_FAILED = "OSRM_FAILED"

def clean_crime_data(df):
    """Cleans known issues in crime.xlsx"""
    df = df.dropna(subset=['timestamp'])
    shifted_mask = df['Unnamed: 10'].notna()
    if shifted_mask.any():
        for idx in df[shifted_mask].index:
            df.loc[idx, 'incident_type'] = df.loc[idx, 'severity']
            df.loc[idx, 'severity'] = 'low'
            df.loc[idx, 'description'] = df.loc[idx, 'safety_score_0_100']
            df.loc[idx, 'safety_score_0_100'] = df.loc[idx, 'Unnamed: 10']
    if 'Unnamed: 10' in df.columns:
        df = df.drop(columns=['Unnamed: 10'])
    return df

def get_time_bucket(dt_str):
    if pd.isna(dt_str):
        return 'day'
    try:
        dt = datetime.fromisoformat(str(dt_str))
        hour = dt.hour
        if TIME_BUCKETS['day'][0] <= hour < TIME_BUCKETS['day'][1]:
            return 'day'
        elif TIME_BUCKETS['evening'][0] <= hour < TIME_BUCKETS['evening'][1]:
            return 'evening'
        else:
            return 'night'
    except Exception:
        return 'day'

def build_hex_time_risk(crime_df, output_path='data/hex_time_risk.csv'):
    crime_df = clean_crime_data(crime_df)
    crime_df['time_bucket'] = crime_df['timestamp'].apply(get_time_bucket)
    
    def to_hex(row):
        try:
            if pd.isna(row['lat']) or pd.isna(row['long']): return None
            return h3.latlng_to_cell(row['lat'], row['long'], H3_RES)
        except Exception:
            return None
            
    crime_df['hex_id'] = crime_df.apply(to_hex, axis=1)
    crime_df = crime_df.dropna(subset=['hex_id'])
    risk_df = crime_df.groupby(['hex_id', 'time_bucket']).size().unstack(fill_value=0).reset_index()
    
    for bucket in ['day', 'evening', 'night']:
        if bucket not in risk_df.columns:
            risk_df[bucket] = 0
            
    for bucket in ['day', 'evening', 'night']:
        max_val = risk_df[bucket].max()
        if max_val > 0:
            risk_df[f'{bucket}_risk'] = (risk_df[bucket] / max_val) * 100
        else:
            risk_df[f'{bucket}_risk'] = 0
            
    risk_df = risk_df[['hex_id', 'day_risk', 'evening_risk', 'night_risk']]
    risk_df.to_csv(output_path, index=False)
    return risk_df

def load_static_scores(geojson_path='data/mumbai_ml_dataset.geojson'):
    gdf = gpd.read_file(geojson_path)
    return gdf[['hex_id', 'safety_score']].set_index('hex_id')['safety_score'].to_dict()

def compute_combined_risk(hex_id, time_bucket, static_scores, hex_time_risk_dict):
    static_score = static_scores.get(hex_id, 50)
    time_risk = 0
    if hex_id in hex_time_risk_dict:
        time_risk = hex_time_risk_dict[hex_id].get(f'{time_bucket}_risk', 0)
    return ALPHA * (100 - static_score) + (1 - ALPHA) * time_risk

def compute_route_cost(mean_risk, max_risk, unsafe_count):
    """Safety-aware objective cost. Lower is better."""
    return (0.5 * mean_risk) + (0.3 * max_risk) + (2.0 * unsafe_count)

def fetch_road_routes(start_lat, start_lng, end_lat, end_lng, waypoints=None, alternatives=True):
    alt_param = "true" if alternatives else "false"
    coords = [f"{start_lng},{start_lat}"]
    if waypoints:
        for lat, lng in waypoints:
            coords.append(f"{lng},{lat}")
    coords.append(f"{end_lng},{end_lat}")
    coords_str = ";".join(coords)
        
    url = f"https://router.project-osrm.org/route/v1/foot/{coords_str}?alternatives={alt_param}&overview=full&geometries=geojson&steps=false"
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"Error calling OSRM API: {e}")
        return []
        
    if data.get("code") != "Ok":
        print(f"OSRM returned non-Ok code: {data.get('code')}")
        return []
        
    routes = []
    for rt in data.get("routes", []):
        coords = [[pt[1], pt[0]] for pt in rt["geometry"]["coordinates"]]
        routes.append({
            "coords": coords,
            "distance_m": rt.get("distance", 0),
            "duration_s": rt.get("duration", 0)
        })
    return routes

def score_route_by_hex_risk(route_coords, time_bucket, static_scores, hex_time_risk_dict, sample_interval_m=150):
    if not route_coords:
        return 0, 0, 0, []
        
    sampled = [route_coords[0]]
    accumulated_dist = 0
    for i in range(1, len(route_coords)):
        pt1 = route_coords[i-1]
        pt2 = route_coords[i]
        d = geodesic(pt1, pt2).meters
        accumulated_dist += d
        if accumulated_dist >= sample_interval_m:
            sampled.append(pt2)
            accumulated_dist = 0
            
    if sampled[-1] != route_coords[-1]:
        sampled.append(route_coords[-1])
        
    total_risk = 0
    max_risk = 0
    unsafe_hexes = set()
    hex_risk_list = []
    
    for lat, lng in sampled:
        h_id = h3.latlng_to_cell(lat, lng, H3_RES)
        risk = compute_combined_risk(h_id, time_bucket, static_scores, hex_time_risk_dict)
        total_risk += risk
        if risk > max_risk:
            max_risk = risk
        hex_risk_list.append((h_id, risk))
        if risk > HIGH_RISK_THRESHOLD:
            unsafe_hexes.add(h_id)
            
    mean_risk = total_risk / len(sampled) if sampled else 0
    unsafe_count = len(unsafe_hexes)
    cost = compute_route_cost(mean_risk, max_risk, unsafe_count)
    return cost, mean_risk, max_risk, unsafe_count, hex_risk_list

def safest_route(start_address, end_address, time_bucket=None, data_dir='data'):
    if not time_bucket:
        hour = datetime.now().hour
        if TIME_BUCKETS['day'][0] <= hour < TIME_BUCKETS['day'][1]: time_bucket = 'day'
        elif TIME_BUCKETS['evening'][0] <= hour < TIME_BUCKETS['evening'][1]: time_bucket = 'evening'
        else: time_bucket = 'night'
            
    crime_path = os.path.join(data_dir, 'crime.xlsx')
    hex_risk_path = os.path.join(data_dir, 'hex_time_risk.csv')
    ml_dataset_path = os.path.join(data_dir, 'mumbai_ml_dataset.geojson')

    crime_df = pd.read_excel(crime_path)
    if os.path.exists(hex_risk_path):
        risk_df = pd.read_csv(hex_risk_path)
    else:
        risk_df = build_hex_time_risk(crime_df, output_path=hex_risk_path)

    hex_time_risk_dict = risk_df.set_index('hex_id').to_dict(orient='index')
    static_scores = load_static_scores(geojson_path=ml_dataset_path)
    
    geolocator = Nominatim(user_agent="girlthon_safe_router", timeout=10)
    def geocode_with_retry(addr):
        try:
            parts = [p.strip() for p in addr.split(',')]
            if len(parts) == 2:
                class DummyLoc: pass
                d = DummyLoc()
                d.latitude = float(parts[0])
                d.longitude = float(parts[1])
                return d
        except ValueError:
            pass
            
        for _ in range(3):
            try:
                time.sleep(1.5)
                res = geolocator.geocode(addr)
                if res: return res
            except Exception:
                time.sleep(2)
        return None

    try:
        start_loc = geocode_with_retry(start_address)
        end_loc = geocode_with_retry(end_address)
        if not start_loc or not end_loc:
            return {"error": "Could not geocode one or both addresses."}
    except Exception as e:
        return {"error": f"Could not geocode: {e}"}

    start_hex = h3.latlng_to_cell(start_loc.latitude, start_loc.longitude, H3_RES)
    end_hex = h3.latlng_to_cell(end_loc.latitude, end_loc.longitude, H3_RES)
    
    if start_hex == end_hex:
        d = geodesic((start_loc.latitude, start_loc.longitude), (end_loc.latitude, end_loc.longitude)).meters
        risk = compute_combined_risk(start_hex, time_bucket, static_scores, hex_time_risk_dict)
        cost = compute_route_cost(risk, risk, 1 if risk > HIGH_RISK_THRESHOLD else 0)
        rt = {
            'path_coords': [[start_loc.latitude, start_loc.longitude], [end_loc.latitude, end_loc.longitude]],
            'cost_score': cost,
            'mean_risk': risk,
            'max_risk': risk,
            'total_risk_score': risk,
            'unsafe_hex_count': 1 if risk > HIGH_RISK_THRESHOLD else 0,
            'duration_s': d / 1.4,
            'distance_m': d,
            'hex_risk_list': [(start_hex, risk)]
        }
        return {
            'safest_route': rt, 'quickest_route': rt,
            'routes_compared': 1, 'detour_attempted': False,
            'forced_detour_used': False, 'iteration_count': 0,
            'stop_reason': StopReason.SUCCESS.value,
            'iteration_history': [], 'time_bucket': time_bucket
        }

    routes = fetch_road_routes(start_loc.latitude, start_loc.longitude, end_loc.latitude, end_loc.longitude)
    if not routes:
        return {"error": "No routes found from OSRM."}
        
    scored_routes = []
    for rt in routes:
        cost, mean_risk, max_risk, unsafe_count, hrl = score_route_by_hex_risk(rt["coords"], time_bucket, static_scores, hex_time_risk_dict)
        rt["cost_score"] = cost
        rt["mean_risk"] = mean_risk
        rt["max_risk"] = max_risk
        rt["unsafe_count"] = unsafe_count
        rt["hex_risk_list"] = hrl
        rt["source"] = "osrm_base"
        scored_routes.append(rt)
        
    detour_attempted = False
    base_route = min(scored_routes, key=lambda x: x["duration_s"])
    base_dist = base_route["distance_m"]
    current_route = min(scored_routes, key=lambda x: x["cost_score"])
    
    waypoints = []
    iteration_history = []
    stop_reason = StopReason.NO_HIGH_RISK
    
    for iteration in range(1, MAX_ITERATIONS + 1):
        hrl = current_route.get("hex_risk_list", [])
        high_risk_hexes = [x for x in hrl if x[1] > HIGH_RISK_THRESHOLD]
        
        if not high_risk_hexes:
            stop_reason = StopReason.NO_HIGH_RISK
            break
            
        highest_risk_hex, max_r = max(high_risk_hexes, key=lambda x: x[1])
        
        # Search ring 1, fallback to ring 2
        neighbors = h3.grid_ring(highest_risk_hex, 1)
        safer_neighbors = []
        for n in neighbors:
            n_risk = compute_combined_risk(n, time_bucket, static_scores, hex_time_risk_dict)
            if n_risk < max_r:
                safer_neighbors.append((n, n_risk))
                
        if not safer_neighbors:
            # Fallback to ring 2
            ring2 = h3.grid_ring(highest_risk_hex, 2)
            for n in ring2:
                n_risk = compute_combined_risk(n, time_bucket, static_scores, hex_time_risk_dict)
                if n_risk < max_r:
                    safer_neighbors.append((n, n_risk))
                    
        if not safer_neighbors:
            stop_reason = StopReason.NO_SAFER_NEIGHBOR
            iteration_history.append({
                "iteration": iteration,
                "worst_hex": {"id": highest_risk_hex, "risk": max_r},
                "status": "Rejected: " + stop_reason.value
            })
            break
            
        detour_attempted = True
        best_neighbor, n_risk = min(safer_neighbors, key=lambda x: x[1])
        wp_lat, wp_lng = h3.cell_to_latlng(best_neighbor)
        
        new_waypoints = waypoints + [(wp_lat, wp_lng)]
        detour_routes = fetch_road_routes(
            start_loc.latitude, start_loc.longitude, 
            end_loc.latitude, end_loc.longitude, 
            waypoints=new_waypoints
        )
        
        improved = False
        if detour_routes:
            for rt in detour_routes:
                cost, mean_risk, max_risk, unsafe_count, hrl2 = score_route_by_hex_risk(rt["coords"], time_bucket, static_scores, hex_time_risk_dict)
                rt["cost_score"] = cost
                rt["mean_risk"] = mean_risk
                rt["max_risk"] = max_risk
                rt["unsafe_count"] = unsafe_count
                rt["hex_risk_list"] = hrl2
                rt["source"] = "forced_detour"
                scored_routes.append(rt)
                
                if cost < current_route["cost_score"] and rt["distance_m"] <= base_dist * MAX_DETOUR_RATIO:
                    history_entry = {
                        "iteration": iteration,
                        "worst_hex": {"id": highest_risk_hex, "risk": max_r},
                        "detour_hex": {"id": best_neighbor, "risk": n_risk},
                        "original_cost": current_route["cost_score"],
                        "candidate_cost": cost,
                        "original_distance": current_route["distance_m"],
                        "candidate_distance": rt["distance_m"],
                        "status": "Accepted"
                    }
                    iteration_history.append(history_entry)
                    current_route = rt
                    improved = True
                    waypoints = new_waypoints
                    break # Take the first route that significantly improves cost
                    
        if not improved:
            stop_reason = StopReason.MAX_DETOUR_RATIO if (detour_routes and all(r.get("distance_m", float('inf')) > base_dist * MAX_DETOUR_RATIO for r in detour_routes)) else StopReason.NO_IMPROVEMENT
            
            # Log failure
            history_entry = {
                "iteration": iteration,
                "worst_hex": {"id": highest_risk_hex, "risk": max_r},
                "detour_hex": {"id": best_neighbor, "risk": n_risk},
                "original_cost": current_route["cost_score"],
                "status": f"Rejected: {stop_reason.value}"
            }
            iteration_history.append(history_entry)
            break
            
    else:
        stop_reason = StopReason.MAX_ITERATIONS

    safe_rt = min(scored_routes, key=lambda x: x["cost_score"])
    quick_rt = min(scored_routes, key=lambda x: x["duration_s"])
    forced_detour_used = (safe_rt.get("source") == "forced_detour") and (safe_rt["cost_score"] < quick_rt["cost_score"])
    
    return {
        'safest_route': {
            'path_coords': safe_rt["coords"],
            'cost_score': safe_rt["cost_score"],
            'mean_risk': safe_rt["mean_risk"],
            'max_risk': safe_rt["max_risk"],
            'total_risk_score': safe_rt["mean_risk"], # backwards compatibility for map drawing
            'unsafe_hex_count': safe_rt["unsafe_count"],
            'duration_s': safe_rt["duration_s"],
            'distance_m': safe_rt["distance_m"],
            'hex_risk_list': safe_rt.get("hex_risk_list", [])
        },
        'quickest_route': {
            'path_coords': quick_rt["coords"],
            'cost_score': quick_rt["cost_score"],
            'mean_risk': quick_rt["mean_risk"],
            'max_risk': quick_rt["max_risk"],
            'total_risk_score': quick_rt["mean_risk"], # backwards compatibility
            'unsafe_hex_count': quick_rt["unsafe_count"],
            'duration_s': quick_rt["duration_s"],
            'distance_m': quick_rt["distance_m"],
            'hex_risk_list': quick_rt.get("hex_risk_list", [])
        },
        'risk_reduction_mean': quick_rt["mean_risk"] - safe_rt["mean_risk"],
        'cost_reduction': quick_rt["cost_score"] - safe_rt["cost_score"],
        'distance_increase_m': safe_rt["distance_m"] - quick_rt["distance_m"],
        'routes_compared': len(scored_routes),
        'detour_attempted': detour_attempted,
        'forced_detour_used': forced_detour_used,
        'iteration_count': len(iteration_history),
        'iteration_history': iteration_history,
        'stop_reason': stop_reason.value if isinstance(stop_reason, StopReason) else stop_reason,
        'time_bucket': time_bucket
    }
