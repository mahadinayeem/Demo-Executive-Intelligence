"""
Build Inverse World Mask for Bangladesh and inject into ceo_national_map.html and cluster_map.html
"""
import json
import os

with open(r"d:\ITL FINAL ADV ANALYSIS\bd_boundary.json", "r", encoding="utf-8") as f:
    bd_data = json.load(f)

# Outer box (world) in [lng, lat]
world_ring = [
    [-180.0, 90.0],
    [-180.0, -90.0],
    [180.0, -90.0],
    [180.0, 90.0],
    [-180.0, 90.0]
]

# Extract all exterior rings of Bangladesh polygons
coords = bd_data['geometry']['coordinates']

# In GeoJSON MultiPolygon: each polygon is a list of rings [ [ [lng,lat],... ], ... ]
# We collect the largest mainland ring as the primary hole
all_rings = []
for poly in coords:
    # poly[0] is exterior ring
    all_rings.append(poly[0])

# Sort rings by vertex count (mainland BD is largest)
all_rings.sort(key=lambda r: len(r), reverse=True)
mainland_ring = all_rings[0]

# Construct Inverse Mask
# In Leaflet / GeoJSON: A Polygon with outer world_ring and inner mainland_ring creates a hole for Bangladesh!
# We can also add secondary island rings as separate holes if desired.
inverse_mask_coords = [world_ring, mainland_ring]

mask_geojson = {
    "type": "Feature",
    "properties": {"name": "Bangladesh_Inverse_Mask"},
    "geometry": {
        "type": "Polygon",
        "coordinates": inverse_mask_coords
    }
}

# Save as bd_mask.js
js_content = f"// Inverse World Mask for Bangladesh\nconst BD_INVERSE_MASK = {json.dumps(mask_geojson)};\nconst BD_OUTLINE = {json.dumps(bd_data)};\n"
with open(r"d:\ITL FINAL ADV ANALYSIS\bd_mask.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print("Created bd_mask.js successfully!")
