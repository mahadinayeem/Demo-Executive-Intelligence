"""
Check Union data in datasets and address fields
"""
import csv, json, sys, os

sys.stdout.reconfigure(encoding='utf-8')

# Check gazipur outlets in module3 or orders
print("Checking Union extraction for Gazipur...")
with open(r'd:\ITL FINAL ADV ANALYSIS\ceo_outlets_D0.js', 'r', encoding='utf-8') as f:
    import re
    text = f.read()
    m = re.search(r'CEO_OUTLETS\[0\]\s*=\s*(\[.*\]);?', text, re.DOTALL)
    if m:
        d0 = json.loads(m.group(1))

gazipur = [o for o in d0 if o[5] and o[5].lower() == 'gazipur']
print(f"Total Gazipur outlets: {len(gazipur)}")
sample_sreepur = [o for o in gazipur if o[16] == 'Sreepur']
print(f"Sample Sreepur outlets: {len(sample_sreepur)}")
for o in sample_sreepur[:5]:
    print(o)
