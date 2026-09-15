import json

# Read bd_boundary.json
with open(r"E:\ITL FINAL ADV ANALYSIS\bd_boundary.json", "r", encoding="utf-8") as f:
    bd_feature = json.load(f)

# The coordinates in GeoJSON are [lng, lat]
# Outer world polygon box: [[lng, lat]]
world_ring = [
    [-180.0, 90.0],
    [-180.0, -90.0],
    [180.0, -90.0],
    [180.0, 90.0],
    [-180.0, 90.0]
]

# Take the main polygon (the largest polygon in MultiPolygon which is mainland BD)
coords = bd_feature['geometry']['coordinates']
# sort polygons by point count to find the main land
sorted_polys = sorted(coords, key=lambda p: len(p[0]), reverse=True)
main_bd_ring = sorted_polys[0][0]

# Construct a single clean Polygon where Ring 0 = World, Ring 1 = Bangladesh Outer Boundary
mask_feature = {
    "type": "Feature",
    "properties": {"name": "Bangladesh_Focus_Mask"},
    "geometry": {
        "type": "Polygon",
        "coordinates": [world_ring, main_bd_ring]
    }
}

# Also inject into map_suite_data.js
with open(r"E:\ITL FINAL ADV ANALYSIS\map_suite_data.js", "r", encoding="utf-8") as f:
    js_text = f.read()

# Remove old BD_BOUNDARY if exists
if "const BD_BOUNDARY" in js_text:
    js_text = js_text.split("const MAP_DATA")[1]
    js_text = "const MAP_DATA" + js_text

new_js = f"const BD_MASK = {json.dumps(mask_feature)};\nconst BD_BOUNDARY = {json.dumps(bd_feature)};\n" + js_text

with open(r"E:\ITL FINAL ADV ANALYSIS\map_suite_data.js", "w", encoding="utf-8") as f:
    f.write(new_js)

print("Generated clean Inverse Mask and saved to map_suite_data.js successfully!")
