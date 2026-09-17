"""
=============================================================================
ITL 1.57M FIELD VISIT HIGH-DENSITY HEATMAP & HUB GENERATOR
=============================================================================
Processes all 1,569,902 GPS check-ins from itl_checkings.csv.
Builds ultra-dense spatial visit points with rich opacity weighting.
=============================================================================
"""

import csv
import json
import math
import sys
from collections import defaultdict
from datetime import datetime

csv.field_size_limit(2147483647)
sys.stdout.reconfigure(encoding='utf-8')

print("[1/4] Loading Reference Centroids...")
DISTRICT_CENTROIDS = [
    (23.8103, 90.4125, "ঢাকা", "Dhaka", "Dhaka"),
    (23.9999, 90.4203, "গাজীপুর সদর", "Gazipur", "Dhaka"),
    (24.0984, 90.4704, "শ্রীপুর", "Gazipur", "Dhaka"),
    (23.6238, 90.5000, "নারায়ণগঞ্জ", "Narayanganj", "Dhaka"),
    (22.3569, 91.7832, "চট্টগ্রাম সদর", "Chattogram", "Chattogram"),
    (23.4607, 91.1809, "কুমিল্লা সদর", "Cumilla", "Chattogram"),
    (24.8949, 91.8687, "সিলেট সদর", "Sylhet", "Sylhet"),
    (25.1368, 92.1220, "জৈন্তাপুর উপজেলা", "Sylhet", "Sylhet"),
    (24.3745, 88.6042, "বোয়ালিয়া", "Rajshahi", "Rajshahi"),
    (24.8465, 89.3777, "বগুড়া সদর", "Bogura", "Rajshahi"),
    (22.8456, 89.5403, "সোনাডাঙ্গা", "Khulna", "Khulna"),
    (23.1664, 89.2081, "যশোর সদর", "Jashore", "Khulna"),
    (22.7010, 90.3535, "বরিশাল সদর", "Barishal", "Barishal"),
    (25.7439, 89.2752, "রংপুর সদর", "Rangpur", "Rangpur"),
    (25.6279, 88.6332, "দিনাজপুর সদর", "Dinajpur", "Rangpur"),
    (24.7471, 90.4203, "কোতোয়ালী", "Mymensingh", "Mymensingh"),
    (24.2500, 89.9167, "টাঙ্গাইল সদর", "Tangail", "Dhaka"),
    (23.9000, 91.1167, "ব্রাহ্মণবাড়িয়া", "Brahmanbaria", "Chattogram"),
    (23.1667, 91.2000, "ফেনী সদর", "Feni", "Chattogram"),
    (21.4272, 92.0058, "কক্সবাজার সদর", "Cox's Bazar", "Chattogram"),
    (24.4500, 91.7667, "মৌলভীবাজার", "Moulvibazar", "Sylhet"),
    (24.3667, 91.4167, "হবিগঞ্জ সদর", "Habiganj", "Sylhet"),
    (24.8667, 91.4000, "সুনামগঞ্জ", "Sunamganj", "Sylhet"),
    (24.3667, 88.6000, "পবা", "Rajshahi", "Rajshahi"),
    (24.1333, 89.0000, "পাবনা সদর", "Pabna", "Rajshahi"),
    (24.4500, 89.7000, "সিরাজগঞ্জ", "Sirajganj", "Rajshahi"),
    (23.9000, 89.1333, "কুষ্টিয়া সদর", "Kushtia", "Khulna"),
    (22.6500, 89.0667, "সাতক্ষীরা", "Satkhira", "Khulna"),
    (22.6833, 90.6500, "ভোলা সদর", "Bhola", "Barishal"),
    (22.6000, 90.1833, "ঝালকাঠি", "Jhalokati", "Barishal"),
    (22.3000, 89.9667, "পিরোজপুর", "Pirojpur", "Barishal"),
    (22.0333, 90.2500, "পটুয়াখালী", "Patuakhali", "Barishal"),
    (25.9000, 89.0000, "কুড়িগ্রাম", "Kurigram", "Rangpur"),
    (25.7500, 88.9000, "নীলফামারী", "Nilphamari", "Rangpur"),
    (26.0333, 88.4667, "ঠাকুরগাঁও", "Thakurgaon", "Rangpur"),
    (26.3333, 88.5500, "পঞ্চগড়", "Panchagarh", "Rangpur"),
    (25.9000, 89.4500, "গাইবান্ধা", "Gaibandha", "Rangpur"),
    (24.9000, 89.9500, "জামালপুর সদর", "Jamalpur", "Mymensingh"),
    (24.9000, 90.6500, "নেত্রকোণা", "Netrokona", "Mymensingh"),
    (24.4333, 90.7833, "কিশোরগঞ্জ", "Kishoreganj", "Dhaka"),
    (23.6000, 89.8500, "ফরিদপুর সদর", "Faridpur", "Dhaka"),
    (23.2333, 90.1500, "মাদারীপুর", "Madaripur", "Dhaka"),
    (23.0000, 89.8333, "গোপালগঞ্জ", "Gopalganj", "Dhaka"),
    (23.2000, 90.3500, "শরীয়তপুর", "Shariatpur", "Dhaka"),
    (23.7500, 89.6500, "রাজবাড়ী", "Rajbari", "Dhaka"),
    (23.8500, 90.0000, "মানিকগঞ্জ", "Manikganj", "Dhaka"),
    (23.5500, 90.5333, "মুন্সীগঞ্জ", "Munshiganj", "Dhaka"),
    (23.9500, 90.7000, "নরসিংদী সদর", "Narsingdi", "Dhaka"),
    (22.8500, 91.1000, "নোয়াখালী", "Noakhali", "Chattogram"),
    (22.9500, 90.8333, "লক্ষ্মীপুর", "Lakshmipur", "Chattogram"),
    (23.2333, 90.6667, "চাঁদপুর সদর", "Chandpur", "Chattogram")
]

def get_nearest_location(lat, lng):
    best_dist = 999999
    best_loc = ("অজ্ঞাত এলাকা", "ঢাকা", "Dhaka")
    for clat, clng, thana, dist, div in DISTRICT_CENTROIDS:
        d = math.hypot(lat - clat, lng - clng)
        if d < best_dist:
            best_dist = d
            best_loc = (thana, dist, div)
    return best_loc

print("[2/4] Reading ALL 1,569,902 visits from itl_checkings.csv...")
grid_density = defaultdict(int)
total_visits_counted = 0

with open('itl_checkings.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        try:
            lat = float(r.get('lat') or 0)
            lng = float(r.get('long') or 0)
        except:
            continue
        if 20.5 <= lat <= 26.7 and 88.0 <= lng <= 92.7:
            # 0.008 degree grid cell (~800m) for continuous lush coverage
            glat = round(lat, 3)
            glng = round(lng, 3)
            grid_density[(glat, glng)] += 1
            total_visits_counted += 1

print(f"Total Valid Visits Processed: {total_visits_counted:,}")
print(f"Total Ultra-Dense Grid Cells: {len(grid_density):,}")

# Build heatmap points: [lat, lng, weight]
max_density = max(grid_density.values()) if grid_density else 1
log_max = math.log1p(max_density)

heat_points = []
for (lat, lng), count in grid_density.items():
    # Weight between 0.35 (base presence) to 1.0 (high traffic corridor)
    w = 0.35 + 0.65 * (math.log1p(count) / log_max)
    heat_points.append([lat, lng, round(w, 3)])

print("[3/4] Extracting Top 300 High-Density Micro-Locations...")
# Sort by visit counts
top_300 = sorted(grid_density.items(), key=lambda x: x[1], reverse=True)[:300]

hubs_data = []
for rank, ((lat, lng), count) in enumerate(top_300, 1):
    thana, dist, div = get_nearest_location(lat, lng)
    hubs_data.append({
        'rank': rank,
        'lat': lat,
        'lng': lng,
        'visits': count,
        'thana': thana,
        'district': dist,
        'division': div,
        'label_bn': f"{thana}, {dist} জেলা, {div} বিভাগ",
        'label_en': f"{thana}, {dist} District, {div} Division"
    })

print(f"Top Hub #1: {hubs_data[0]['label_bn']} -> {hubs_data[0]['visits']:,} visits")

payload = {
    'meta': {
        'company': 'Ispahani Tea Limited',
        'period': 'মে - আগস্ট ২০২৬ (৪ মাসের অডিট সাইকেল)',
        'period_en': 'May - August 2026 (4-Month Audit Cycle)',
        'total_visits': total_visits_counted,
        'total_grid_cells': len(grid_density),
        'top_hubs_count': len(hubs_data),
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    'heat_points': heat_points,
    'top_300_hubs': hubs_data
}

with open('itl_visit_heatmap_data.js', 'w', encoding='utf-8') as f:
    f.write('window.ITL_VISIT_MAP_DATA = ' + json.dumps(payload, ensure_ascii=False) + ';\n')

print(f"[4/4] Written {len(heat_points):,} points to itl_visit_heatmap_data.js successfully!")
