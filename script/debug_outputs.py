import pandas as pd
import h3
from safe_route import safest_route

print("\n--- 1. Day vs Evening vs Night for Andheri -> Colaba ---")
start = "19.119, 72.846"
end = "18.919, 72.827"
for tb in ['day', 'evening', 'night']:
    res = safest_route(start, end, time_bucket=tb)
    if "error" in res:
        print(f"[{tb.upper()}] Error: {res['error']}")
        continue
    safe = res['safest_route']
    quick = res['quickest_route']
    print(f"[{tb.upper()}] Quickest Risk: {quick['total_risk_score']:.2f} | Safest Risk: {safe['total_risk_score']:.2f}")

print("\n--- 2. Borivali -> Colaba Iterative Detour Comparison ---")
start = "19.229, 72.859"
end = "18.906, 72.815"
res = safest_route(start, end, time_bucket='night')
if "error" in res:
    print(f"Error: {res['error']}")
else:
    safe = res['safest_route']
quick = res['quickest_route']
print(f"Detour Attempted: {res['detour_attempted']}, Forced Detour Chosen: {res['forced_detour_used']}")
print(f"Quickest Risk: {quick['total_risk_score']:.2f}, Safest Risk: {safe['total_risk_score']:.2f}")
print("Quickest Route Hex-by-Hex:")
for h_id, risk in quick['hex_risk_list']:
    if risk > 0:
        print(f"  {h_id}: {risk:.1f}")
print("Safest Route Hex-by-Hex:")
for h_id, risk in safe['hex_risk_list']:
    if risk > 0:
        print(f"  {h_id}: {risk:.1f}")

print("\n--- 3. High-Crime Hex Pair Map Generation ---")
df = pd.read_csv('data/hex_time_risk.csv')
high_risk_hex = df.sort_values('night_risk', ascending=False).iloc[0]['hex_id']
lat, lng = h3.cell_to_latlng(high_risk_hex)
start = f"{lat-0.02}, {lng-0.02}"
end = f"{lat+0.02}, {lng+0.02}"
print(f"Generating map for High-Crime Area: {start} -> {end}")
import os
os.system(f'venv\\Scripts\\python.exe script\\run_route_demo.py --start "{start}" --end "{end}" --time night')
