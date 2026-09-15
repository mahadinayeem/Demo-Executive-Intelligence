import json

# Read bd_boundary.json
with open(r"E:\ITL FINAL ADV ANALYSIS\bd_boundary.json", "r", encoding="utf-8") as f:
    bd_feature = json.load(f)

# Read map_suite_data.js
with open(r"E:\ITL FINAL ADV ANALYSIS\map_suite_data.js", "r", encoding="utf-8") as f:
    existing_js = f.read()

# Append BD Boundary to map_suite_data.js
# Create inverted polygon (World box with BD cut out) for dark/dim focus mask
world_polygon = [
    [-90, -180],
    [-90, 180],
    [90, 180],
    [90, -180],
    [-90, -180]
]

# Write updated map_suite_data.js
boundary_str = f"const BD_BOUNDARY = {json.dumps(bd_feature)};\n"

with open(r"E:\ITL FINAL ADV ANALYSIS\map_suite_data.js", "w", encoding="utf-8") as f:
    f.write(boundary_str + existing_js)

print("Injected BD_BOUNDARY into map_suite_data.js successfully!")
