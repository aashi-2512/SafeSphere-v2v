from safe_route import safest_route

print("=== A: Coordinates (as used before the production upgrades) ===")
res = safest_route("19.229, 72.859", "18.906, 72.815", time_bucket='night')
if "error" in res:
    print(f"Error: {res['error']}")
else:
    q = res['quickest_route']
    s = res['safest_route']
    print(f"Forced Detour: {res['forced_detour_used']}")
    print(f"Iterations: {res['iteration_count']}  Stop: {res['stop_reason']}")
    print(f"Quickest -> Cost: {q['cost_score']:.3f}  MeanRisk: {q['mean_risk']:.2f}  MaxRisk: {q['max_risk']:.2f}  Unsafe: {q['unsafe_hex_count']}")
    print(f"Safest   -> Cost: {s['cost_score']:.3f}  MeanRisk: {s['mean_risk']:.2f}  MaxRisk: {s['max_risk']:.2f}  Unsafe: {s['unsafe_hex_count']}")
    print(f"Start point: {19.229}, {72.859}")
    for step in res.get('iteration_history', []):
        print(f"  Iter {step['iteration']}: worst={step['worst_hex']['risk']:.1f} | {step['status']}")

print()
print("=== B: Named addresses (Borivali Railway Station -> Colaba) ===")
# First, geocode to find out what lat/lng Nominatim actually resolves to
from geopy.geocoders import Nominatim
import time
geo = Nominatim(user_agent="girlthon_diag", timeout=10)
time.sleep(1.5)
start_loc = geo.geocode("Borivali Railway Station, Mumbai")
time.sleep(1.5)
end_loc = geo.geocode("Colaba, Mumbai")
print(f"Geocoded start: {start_loc.latitude:.4f}, {start_loc.longitude:.4f}")
print(f"Geocoded end:   {end_loc.latitude:.4f}, {end_loc.longitude:.4f}")
print(f"Raw coords used before: 19.2290, 72.8590 / 18.9060, 72.8150")
print()

res2 = safest_route("Borivali Railway Station, Mumbai", "Colaba, Mumbai", time_bucket='night')
if "error" in res2:
    print(f"Error: {res2['error']}")
else:
    q = res2['quickest_route']
    s = res2['safest_route']
    print(f"Forced Detour: {res2['forced_detour_used']}")
    print(f"Iterations: {res2['iteration_count']}  Stop: {res2['stop_reason']}")
    print(f"Quickest -> Cost: {q['cost_score']:.3f}  MeanRisk: {q['mean_risk']:.2f}  MaxRisk: {q['max_risk']:.2f}  Unsafe: {q['unsafe_hex_count']}")
    print(f"Safest   -> Cost: {s['cost_score']:.3f}  MeanRisk: {s['mean_risk']:.2f}  MaxRisk: {s['max_risk']:.2f}  Unsafe: {s['unsafe_hex_count']}")
    for step in res2.get('iteration_history', []):
        print(f"  Iter {step['iteration']}: worst={step['worst_hex']['risk']:.1f} | {step['status']}")
