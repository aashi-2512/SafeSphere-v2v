import argparse
import folium
import os
from safe_route import safest_route

def generate_map(result, output_filename):
    safe_rt = result.get('safest_route')
    quick_rt = result.get('quickest_route')
    
    if not safe_rt or not quick_rt:
        print("Invalid result dict, skipping map generation.")
        return
        
    start_coord = quick_rt['path_coords'][0]
    m = folium.Map(location=start_coord, zoom_start=14)
    
    # Plot quickest route (Red)
    folium.PolyLine(
        quick_rt['path_coords'], 
        color="red", 
        weight=4, 
        opacity=0.8,
        tooltip="Quickest Route"
    ).add_to(m)
    
    # Plot safest route (Green) if different
    is_diff = safe_rt['path_coords'] != quick_rt['path_coords']
    if is_diff:
        folium.PolyLine(
            safe_rt['path_coords'], 
            color="green", 
            weight=6, 
            opacity=0.7,
            tooltip="Safest Route"
        ).add_to(m)
        
    # Start and End Markers
    folium.Marker(safe_rt['path_coords'][0], popup="Start", icon=folium.Icon(color="blue")).add_to(m)
    folium.Marker(safe_rt['path_coords'][-1], popup="End", icon=folium.Icon(color="red")).add_to(m)
    
    from safe_route import load_static_scores, build_hex_time_risk, compute_combined_risk
    import pandas as pd
    import h3
    
    def get_color(risk):
        # 0 -> light red/pink, 100 -> dark red
        r = int(255 - (255 - 139) * (risk / 100))
        g = int(204 - (204 - 0) * (risk / 100))
        b = int(204 - (204 - 0) * (risk / 100))
        return f"#{r:02x}{g:02x}{b:02x}"
        
    static_scores = load_static_scores()
    if os.path.exists('data/hex_time_risk.csv'):
        risk_df = pd.read_csv('data/hex_time_risk.csv')
    else:
        crime_df = pd.read_excel('data/crime.xlsx')
        risk_df = build_hex_time_risk(crime_df)
    hex_time_risk_dict = risk_df.set_index('hex_id').to_dict(orient='index')
    
    fg = folium.FeatureGroup(name="Full City Safety Map", show=False)
    
    hex_count = 0
    for h_id in static_scores.keys():
        try:
            boundary = h3.cell_to_boundary(h_id)
            risk = compute_combined_risk(h_id, result['time_bucket'], static_scores, hex_time_risk_dict)
            color = get_color(risk)
            
            folium.Polygon(
                locations=boundary,
                color=color,
                weight=1,
                fill=True,
                fill_color=color,
                fill_opacity=0.35,
                tooltip=f"Danger Score: {risk:.1f}"
            ).add_to(fg)
            hex_count += 1
        except Exception:
            pass
            
    fg.add_to(m)
    print(f"Rendered {hex_count} hexes in Full City Safety Map layer.")
    folium.LayerControl().add_to(m)
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    m.save(output_filename)
    print(f"Saved map to {output_filename}")

def main():
    parser = argparse.ArgumentParser(description="Safe Route Visualizer")
    parser.add_argument("--start", required=True, help="Start address or coordinates")
    parser.add_argument("--end", required=True, help="End address or coordinates")
    parser.add_argument("--time", choices=['day', 'evening', 'night'], default='night', help="Time bucket")
    parser.add_argument("--output", help="Output HTML file name")
    
    args = parser.parse_args()
    
    print(f"Routing from '{args.start}' to '{args.end}' at {args.time}...")
    res = safest_route(args.start, args.end, time_bucket=args.time)
    
    if "error" in res:
        print(f"Error: {res['error']}")
        return
        
    safe_rt = res['safest_route']
    quick_rt = res['quickest_route']
    
    print("\n--- Route Summary ---")
    print(f"Time Bucket: {res['time_bucket']}")
    print(f"Routes Compared: {res['routes_compared']}")
    print(f"Forced Detour Used: {res['forced_detour_used']}")
    print("-" * 20)
    print(f"QUICKEST ROUTE:")
    print(f"  Risk Score: {quick_rt['total_risk_score']:.2f}")
    print(f"  Distance:   {quick_rt['distance_m']}m")
    print(f"  Duration:   {quick_rt['duration_s']/60:.1f} min")
    print(f"  Unsafe Hex: {quick_rt['unsafe_hex_count']}")
    
    print(f"\nSAFEST ROUTE:")
    print(f"  Risk Score: {safe_rt['total_risk_score']:.2f}")
    print(f"  Distance:   {safe_rt['distance_m']}m")
    print(f"  Duration:   {safe_rt['duration_s']/60:.1f} min")
    print(f"  Unsafe Hex: {safe_rt['unsafe_hex_count']}")
    
    if safe_rt['path_coords'] != quick_rt['path_coords']:
        print("\n=> Divergence: Safest route found a different path to reduce risk!")
    else:
        print("\n=> No Divergence: Safest route is identical to quickest route.")
        
    filename = args.output
    if not filename:
        clean_start = "".join(c if c.isalnum() else "_" for c in args.start.split(",")[0]).strip("_")
        clean_end = "".join(c if c.isalnum() else "_" for c in args.end.split(",")[0]).strip("_")
        filename = f"output/route_map_{clean_start}_{clean_end}_{args.time}.html"
        
    generate_map(res, filename)

if __name__ == "__main__":
    main()
