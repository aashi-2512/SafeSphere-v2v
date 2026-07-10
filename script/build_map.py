import geopandas as gpd
import folium
import json
import re

gdf = gpd.read_file("data/mumbai_ml_dataset.geojson")
gdf = gdf.to_crs(epsg=4326)

# Percentile-based buckets for visual differentiation (real scores, relative coloring)
q20, q40, q60, q80 = gdf["safety_score"].quantile([0.2, 0.4, 0.6, 0.8])

def get_color(score):
    if score <= q20:
        return "#c0392b"   # red - bottom 20%
    elif score <= q40:
        return "#e67e22"   # orange
    elif score <= q60:
        return "#f1c40f"   # yellow
    elif score <= q80:
        return "#82c46c"   # light green
    else:
        return "#1e8449"   # dark green - top 20%

center = [gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()]

m = folium.Map(location=center, zoom_start=11, tiles="cartodbpositron")

for _, row in gdf.iterrows():
    color = get_color(row["safety_score"])
    popup_html = f"""
    <div style='font-family: sans-serif; font-size: 13px; min-width:200px'>
      <b>Safety Score: {row['safety_score']:.1f}/100</b><br>
      <hr style='margin:4px 0'>
      Crime incidents in hex: <b>{int(row['crime_count'])}</b><br>
      Nearest police: {row['police_distance']:.0f} m<br>
      Nearest hospital: {row['hospital_distance']:.0f} m<br>
      Nearest railway: {row['railway_distance']:.0f} m<br>
      Nearest metro: {row['metro_distance']:.0f} m<br>
      Nearest bus stop: {row['bus_stop_distance']:.0f} m<br>
      Restaurants: {int(row['restaurants'])} | Parks: {int(row['parks'])}<br>
      Schools: {int(row['schools'])} | Pharmacies: {int(row['pharmacies'])}
    </div>
    """
    gj = folium.GeoJson(
        row["geometry"].__geo_interface__,
        style_function=lambda feat, color=color: {
            "fillColor": color,
            "color": "#333333",
            "weight": 0.5,
            "fillOpacity": 0.65,
        },
        highlight_function=lambda feat: {"weight": 2, "color": "#000000"},
        tooltip=folium.Tooltip(f"Score: {row['safety_score']:.1f}"),
        popup=folium.Popup(popup_html, max_width=280),
    )
    gj.add_to(m)

# Legend
legend_html = """
<div style="position: fixed; bottom: 30px; left: 30px; z-index: 9999;
     background: white; padding: 12px 16px; border-radius: 8px;
     box-shadow: 0 2px 8px rgba(0,0,0,0.3); font-family: sans-serif; font-size: 13px;">
  <b>Relative Safety Score</b><br>(percentile within Mumbai)<br>
  <div style="margin-top:6px">
    <span style="background:#1e8449;width:12px;height:12px;display:inline-block;margin-right:6px;"></span>Top 20% (safest)<br>
    <span style="background:#82c46c;width:12px;height:12px;display:inline-block;margin-right:6px;"></span>60&ndash;80%<br>
    <span style="background:#f1c40f;width:12px;height:12px;display:inline-block;margin-right:6px;"></span>40&ndash;60%<br>
    <span style="background:#e67e22;width:12px;height:12px;display:inline-block;margin-right:6px;"></span>20&ndash;40%<br>
    <span style="background:#c0392b;width:12px;height:12px;display:inline-block;margin-right:6px;"></span>Bottom 20% (least safe)<br>
  </div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

out_path = "data/mumbai_safety_map.html"
m.save(out_path)

# Inject a client-side location search box (Leaflet Control Geocoder, Nominatim)
# Runs in the USER's browser, not this sandbox, so no network restriction issue here.
with open(out_path, "r") as f:
    html = f.read()

map_var_match = re.search(r'var (map_\w+) = L\.map', html)
map_var = map_var_match.group(1)

search_injection = f"""
<link rel="stylesheet" href="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.css" />
<script src="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {{
  setTimeout(function() {{
    L.Control.geocoder({{
      defaultMarkGeocode: true,
      placeholder: 'Search a location in Mumbai...',
      position: 'topleft'
    }}).addTo({map_var});
  }}, 500);
}});
</script>
</body>
"""
html = html.replace("</body>", search_injection)

with open(out_path, "w") as f:
    f.write(html)

print("Map saved to", out_path)
print(f"Score buckets - 20%: {q20:.1f}, 40%: {q40:.1f}, 60%: {q60:.1f}, 80%: {q80:.1f}")