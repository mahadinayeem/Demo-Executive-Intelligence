"""
Audit Gazipur Thanas in ceo_outlets_D0.js
"""
import json, re

with open(r'd:\ITL FINAL ADV ANALYSIS\ceo_outlets_D0.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'CEO_OUTLETS\[0\]\s*=\s*(\[.*\]);?', text, re.DOTALL)
if m:
    d0 = json.loads(m.group(1))

gazipur = [o for o in d0 if o[5] and o[5].lower() == 'gazipur']
print(f"Total Gazipur outlets: {len(gazipur)}")

thanas = {}
for o in gazipur:
    t = o[16]
    thanas[t] = thanas.get(t, 0) + 1

for t, c in sorted(thanas.items(), key=lambda x: x[1], reverse=True):
    print(f"  {t}: {c}")
