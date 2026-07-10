import json
from safe_route import safest_route

res = safest_route("19.229, 72.859", "18.906, 72.815", time_bucket='night')
if "error" in res:
    print(res["error"])
else:
    print(f"Iterations: {res.get('iteration_count')}")
    print(f"Stop Reason: {res.get('stop_reason')}")
    print(f"Forced Detour: {res.get('forced_detour_used')}")
    print(f"Cost Reduction: {res.get('cost_reduction'):.2f}")
    print(f"Risk Reduction: {res.get('risk_reduction_mean'):.2f}")
    print(f"Distance Increase: {res.get('distance_increase_m')} m")
    
    print("\n--- Iteration History ---")
    for step in res.get('iteration_history', []):
        print(f"Iteration {step['iteration']}:")
        print(f"  Worst Hex: {step['worst_hex']['risk']:.1f}")
        if 'detour_hex' in step:
            print(f"  Detour Hex: {step['detour_hex']['risk']:.1f}")
            print(f"  Cost: {step['original_cost']:.2f} -> {step.get('candidate_cost', 'N/A')}")
        print(f"  Status: {step['status']}")
        print()
