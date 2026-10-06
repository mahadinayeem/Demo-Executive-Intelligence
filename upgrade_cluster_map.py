"""
Upgrade cluster_map.html with Google Streets & Satellite, and 3-tier colors (Ordered / Visited No Order / Untapped)
"""
import re

path = r'd:\ITL FINAL ADV ANALYSIS\cluster_map.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update outlet rendering logic in cluster_map.html to use 3 tiers:
# 🟢 Ordered Outlets (#10b981)
# 🟡 Visited Outlets (No Order) (#f59e0b)
# 🔴 Untapped Outlets (#ef4444)
old_outlet_draw = '''        const visits = o[6] || 0;
        const rev = o[8] || 0;
        const active = visits > 0;

        const m = L.circleMarker([lat, lng], {
          radius: 5,
          fillColor: active ? '#10b981' : '#dc2626',
          color: '#ffffff',
          weight: 1,
          opacity: 1,
          fillOpacity: 0.9
        });'''

new_outlet_draw = '''        const visits = o[6] || 0;
        const rev = o[8] || 0;
        const orders = o[13] || 0;
        
        let tierName = 'Ordered Outlet';
        let dotColor = '#10b981'; // Green
        if (rev > 0 || orders > 0) {
          tierName = 'Ordered Outlet';
          dotColor = '#10b981';
        } else if (visits > 0) {
          tierName = 'Visited (No Order)';
          dotColor = '#f59e0b';
        } else {
          tierName = 'Untapped Outlet (0 Visits)';
          dotColor = '#ef4444';
        }

        const m = L.circleMarker([lat, lng], {
          radius: 6,
          fillColor: dotColor,
          color: '#ffffff',
          weight: 1.5,
          opacity: 1,
          fillOpacity: 0.95
        });'''

if old_outlet_draw in content:
    content = content.replace(old_outlet_draw, new_outlet_draw)

# Add Google Street Map base layer to cluster_map.html
if "L.tileLayer('https://mt1.google.com/vt/lyrs=m" not in content:
    content = content.replace(
        "L.control.zoom({ position: 'bottomright' }).addTo(map);",
        "L.control.zoom({ position: 'bottomright' }).addTo(map);\n  L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', { maxZoom: 20, subdomains: ['mt0','mt1','mt2','mt3'], attribution: '© Google Maps' }).addTo(map);"
    )

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

with open(r'd:\ITL FINAL ADV ANALYSIS\itl_retail_footprint_cluster_map.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Upgraded cluster_map.html and itl_retail_footprint_cluster_map.html successfully!")
