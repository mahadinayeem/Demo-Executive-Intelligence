"""
Standardize and Consolidate all Thana names across 8 divisions to match BBS official naming
"""
import json, re, sys, os
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# Canonical clean mapping for thana names
CANONICAL_THANAS = {
    'gazipursadar': 'Gazipur Sadar',
    'gazipur sadar': 'Gazipur Sadar',
    'kaliganjpaurashava': 'Kaliganj',
    'kaliganj': 'Kaliganj',
    'sreepur': 'Sreepur',
    'kaliakair': 'Kaliakair',
    'kapasia': 'Kapasia',
    'tangailsadar': 'Tangail Sadar',
    'faridpursadar': 'Faridpur Sadar',
    'kishoreganjsadar': 'Kishoreganj Sadar',
    'manikganjsadar': 'Manikganj Sadar',
    'munshiganjsadar': 'Munshiganj Sadar',
    'narayangobjsadar': 'Narayanganj Sadar',
    'narayanganjsadar': 'Narayanganj Sadar',
    'narsingdisadar': 'Narsingdi Sadar',
    'rajbarisadar': 'Rajbari Sadar',
    'gopalganjsadar': 'Gopalganj Sadar',
    'madaripursadar': 'Madaripur Sadar',
    'shariatpursadar': 'Shariatpur Sadar',
    'mymensinghsadar': 'Mymensingh Sadar',
    'rajshahisadar': 'Rajshahi Sadar',
    'sylhetsadar': 'Sylhet Sadar',
    'rangpursadar': 'Rangpur Sadar',
    'khulnasadar': 'Khulna Sadar',
    'barishalsadar': 'Barishal Sadar',
    'chattogramsadar': 'Chattogram Sadar',
    'comillasadar': 'Cumilla Sadar',
    'cumillasadar': 'Cumilla Sadar',
    'chittagongsadar': 'Chattogram Sadar',
    'chittagong': 'Chattogram Sadar',
    'kotwali': 'Kotwali',
}

def clean_thana_name(thana_raw):
    if not thana_raw:
        return 'Sadar'
    raw_clean = thana_raw.lower().replace(' ', '').replace('_', '').replace('-', '')
    
    if raw_clean in CANONICAL_THANAS:
        return CANONICAL_THANAS[raw_clean]
    
    # If ends with Sadar or Paurashava without space, add space or clean
    if raw_clean.endswith('paurashava'):
        base = raw_clean.replace('paurashava', '')
        return base.capitalize()
    
    if raw_clean.endswith('sadar') and len(raw_clean) > 5:
        base = raw_clean.replace('sadar', '')
        return f"{base.capitalize()} Sadar"
        
    return thana_raw.strip()

DIV_NAMES = ['Dhaka', 'Chattogram', 'Rajshahi', 'Khulna', 'Barishal', 'Sylhet', 'Rangpur', 'Mymensingh']

for didx in range(8):
    fpath = f'd:\\ITL FINAL ADV ANALYSIS\\ceo_outlets_D{didx}.js'
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()

    m = re.search(r'CEO_OUTLETS\[\d+\]\s*=\s*(\[.*\]);?', text, re.DOTALL)
    if not m:
        continue
    
    outlets = json.loads(m.group(1))
    for o in outlets:
        # o[16] is thana
        o[16] = clean_thana_name(o[16])

    new_js = f"// {DIV_NAMES[didx]} Division Outlets (Standardized BBS Hierarchy)\nCEO_OUTLETS[{didx}]=" + json.dumps(outlets, ensure_ascii=False) + ";\n"
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_js)

print("Standardized thana names across all 8 divisions!")

# Verify Gazipur specifically
with open(r'd:\ITL FINAL ADV ANALYSIS\ceo_outlets_D0.js', 'r', encoding='utf-8') as f:
    text = f.read()
m = re.search(r'CEO_OUTLETS\[0\]\s*=\s*(\[.*\]);?', text, re.DOTALL)
d0 = json.loads(m.group(1))
gazipur = [o for o in d0 if o[5] and o[5].lower() == 'gazipur']

gz_thanas = defaultdict(int)
for o in gazipur:
    gz_thanas[o[16]] += 1

print(f"\nOfficial Gazipur Thanas ({len(gz_thanas)} total):")
for t, c in sorted(gz_thanas.items(), key=lambda x: x[1], reverse=True):
    print(f"  ✅ {t}: {c:,} outlets")
