"""
Audit Gazipur Outlets, Coordinates, and Thanas in CEO_OUTLETS[0] (Dhaka Division)
"""
import json, re, sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'd:\ITL FINAL ADV ANALYSIS\ceo_outlets_D0.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'CEO_OUTLETS\[0\]\s*=\s*(\[.*\]);?', text, re.DOTALL)
if m:
    outlets = json.loads(m.group(1))

gazipur_outlets = [o for o in outlets if o[5] and o[5].lower() == 'gazipur']
print(f"Total Gazipur Outlets: {len(gazipur_outlets)}")

# Check distinct thanas in Gazipur
thana_counts = {}
for o in gazipur_outlets:
    t = o[16] if len(o) > 16 else 'Unknown'
    thana_counts[t] = thana_counts.get(t, 0) + 1

print("\nThanas under Gazipur in raw dataset:")
for t, c in sorted(thana_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  - {t}: {c} outlets")

# Check GPS bounds of Gazipur in dataset
# Gazipur true bounds: Lat ~ 23.88 to 24.35, Lng ~ 90.15 to 90.72
out_of_bounds = []
for o in gazipur_outlets:
    lat, lng = o[0], o[1]
    if lat < 23.85 or lat > 24.40 or lng < 90.10 or lng > 90.75:
        out_of_bounds.append(o)

print(f"\nOutlets with GPS outside Gazipur actual boundary: {len(out_of_bounds)}")
for o in out_of_bounds[:10]:
    print(f"  ID: {o[2]} | {o[3]} | Lat: {o[0]}, Lng: {o[1]} | Dist: {o[5]} | Thana: {o[16] if len(o)>16 else ''}")
