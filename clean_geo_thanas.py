import json

with open('bd_thanas_geo.js', 'r', encoding='utf-8') as f:
    text = f.read()
start = text.find('{')
end = text.rfind('}') + 1
geo = json.loads(text[start:end])

# Let's inspect Gazipur polygons:
# Merge Kaliganj and KaliganjPaurashava into a single Kaliganj feature, or keep standard 5 thanas:
new_features = []
kaliganj_features = []

for f in geo['features']:
    props = f['properties']
    if props.get('district') == 'Gazipur':
        if props.get('thana') == 'GazipurSadar':
            f['properties']['thana'] = 'Gazipur Sadar'
            new_features.append(f)
        elif props.get('thana') in ['Kaliganj', 'KaliganjPaurashava']:
            kaliganj_features.append(f)
        else:
            new_features.append(f)
    else:
        new_features.append(f)

# For Kaliganj: create a MultiPolygon or Polygon containing both Kaliganj and KaliganjPaurashava
if kaliganj_features:
    combined_coords = []
    for kf in kaliganj_features:
        gtype = kf['geometry']['type']
        if gtype == 'Polygon':
            combined_coords.append(kf['geometry']['coordinates'])
        elif gtype == 'MultiPolygon':
            combined_coords.extend(kf['geometry']['coordinates'])
    
    kaliganj_feat = {
        "type": "Feature",
        "properties": {
            "division": "Dhaka",
            "district": "Gazipur",
            "thana": "Kaliganj"
        },
        "geometry": {
            "type": "MultiPolygon" if len(combined_coords) > 1 else "Polygon",
            "coordinates": combined_coords if len(combined_coords) > 1 else combined_coords[0]
        }
    }
    new_features.append(kaliganj_feat)

geo['features'] = new_features

with open('bd_thanas_geo.js', 'w', encoding='utf-8') as f:
    f.write('const BD_THANAS_GEO = ' + json.dumps(geo, ensure_ascii=False) + ';\n')

print("Updated bd_thanas_geo.js successfully with exact 5 Gazipur thanas!")
