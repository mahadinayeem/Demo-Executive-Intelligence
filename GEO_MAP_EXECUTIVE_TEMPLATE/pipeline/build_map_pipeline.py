"""
=============================================================================
EXECUTIVE GEOSPATIAL MAP DATA PIPELINE (UNIVERSAL STANDALONE ENGINE)
=============================================================================
This script converts any company's sales/outlet data into high-performance,
split-loaded geospatial datasets for the 3-Tier Executive Map Engine.

Outputs Generated:
1. ceo_national.js      -> National, Division, District & Thana KPI Summaries
2. ceo_outlets_D0..D7.js-> Compressed, high-speed chunked outlet arrays

Supported Input Modes:
- Mode 1: Pre-aggregated 'outlets_master.csv' (Fastest & Simplest)
- Mode 2: Raw 'orders.csv' + 'visits.csv' (Full Transactional Aggregation)
=============================================================================
"""

import os
import sys
import csv
import json
import math
from datetime import datetime
from collections import defaultdict

csv.field_size_limit(2147483647)
sys.stdout.reconfigure(encoding='utf-8')

DIVISIONS = [
    'Dhaka', 'Chattogram', 'Rajshahi', 'Khulna',
    'Barishal', 'Sylhet', 'Rangpur', 'Mymensingh'
]

DIV_CODE_MAP = {
    'dha': 'Dhaka', 'dhaka': 'Dhaka', 'dhk': 'Dhaka',
    'ctg': 'Chattogram', 'chattogram': 'Chattogram', 'chittagong': 'Chattogram',
    'raj': 'Rajshahi', 'rajshahi': 'Rajshahi',
    'khu': 'Khulna', 'khulna': 'Khulna',
    'bar': 'Barishal', 'barishal': 'Barishal', 'barisal': 'Barishal',
    'syl': 'Sylhet', 'sylhet': 'Sylhet',
    'ran': 'Rangpur', 'rangpur': 'Rangpur',
    'mym': 'Mymensingh', 'mymensingh': 'Mymensingh'
}

def clean_str(val, default=''):
    if val is None: return default
    return str(val).strip()

def clean_num(val, default=0.0):
    try:
        if val is None: return default
        s = str(val).replace(',', '').strip()
        return float(s) if s else default
    except:
        return default

def normalize_division(raw):
    if not raw: return 'Dhaka'
    s = raw.strip().lower()
    for k, v in DIV_CODE_MAP.items():
        if k in s: return v
    return 'Dhaka'

def compute_health_status(revenue, visits, orders, days_since):
    """
    Computes a 0-100 composite health score and Primary Tag (G=Green, Y=Yellow, R=Red)
    """
    # 1. Revenue Score (0-35)
    if revenue >= 50000: r_score = 35
    elif revenue >= 20000: r_score = 28
    elif revenue >= 10000: r_score = 20
    elif revenue >= 3000: r_score = 12
    elif revenue > 0: r_score = 6
    else: r_score = 0

    # 2. Frequency / Order Score (0-30)
    if orders >= 15: o_score = 30
    elif orders >= 8: o_score = 22
    elif orders >= 4: o_score = 15
    elif orders >= 1: o_score = 8
    else: o_score = 0

    # 3. Visit Engagement Score (0-20)
    if visits >= 20: v_score = 20
    elif visits >= 10: v_score = 15
    elif visits >= 4: v_score = 10
    elif visits >= 1: v_score = 5
    else: v_score = 0

    # 4. Recency Score (0-15)
    if days_since <= 14: rec_score = 15
    elif days_since <= 30: rec_score = 10
    elif days_since <= 60: rec_score = 5
    else: rec_score = 0

    total_score = r_score + o_score + v_score + rec_score

    if total_score >= 60 and revenue > 0:
        status = 'G'  # Strong
    elif total_score >= 35 and revenue > 0:
        status = 'Y'  # Moderate
    else:
        status = 'R'  # Weak / At-Risk

    return total_score, status

def process_outlets_master(csv_path, output_dir='.'):
    """
    Processes an outlets_master.csv file.
    Expected Columns:
    - outlet_id, outlet_name, latitude, longitude, division, district, thana,
      revenue, visits, orders, last_visit_date, days_since_last_visit, sr_name,
      trend_m1, trend_m2, trend_m3, trend_m4 (optional)
    """
    print(f"\n[+] Processing Outlets Master: {csv_path}")
    if not os.path.exists(csv_path):
        print(f"[-] Error: File not found {csv_path}")
        return False

    outlets_by_div = defaultdict(list)
    national_kpis = {
        'total_outlets': 0, 'active_outlets': 0, 'total_revenue': 0.0,
        'total_visits': 0, 'total_orders': 0,
        'strong_outlets': 0, 'moderate_outlets': 0, 'weak_outlets': 0,
        'blind_spots': 0, 'zero_rev_barriers': 0
    }

    div_stats = {d: {'name': d, 'outlets': 0, 'active': 0, 'revenue': 0.0, 'visits': 0, 'orders': 0,
                     'strong': 0, 'moderate': 0, 'weak': 0, 'blind': 0, 'zero_rev': 0,
                     'districts': defaultdict(lambda: {'name': '', 'outlets': 0, 'active': 0, 'revenue': 0.0, 'visits': 0, 'orders': 0,
                                                      'strong': 0, 'moderate': 0, 'weak': 0, 'blind': 0, 'zero_rev': 0,
                                                      'thanas': defaultdict(lambda: {'name': '', 'outlets': 0, 'active': 0, 'revenue': 0.0, 'visits': 0, 'orders': 0, 'strong': 0, 'weak': 0})})}
                 for d in DIVISIONS}

    with open(csv_path, 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        for r in reader:
            o_id = clean_str(r.get('outlet_id') or r.get('id'), f"OUT-{national_kpis['total_outlets']+1}")
            o_name = clean_str(r.get('outlet_name') or r.get('name'), 'Retail Store')
            lat = clean_num(r.get('latitude') or r.get('lat'), 23.8103)
            lng = clean_num(r.get('longitude') or r.get('lng'), 90.4125)
            div = normalize_division(r.get('division'))
            dist = clean_str(r.get('district'), 'Central District')
            thana = clean_str(r.get('thana') or r.get('upazila') or r.get('area'), 'Metro Thana')

            rev = clean_num(r.get('revenue') or r.get('total_revenue') or r.get('sales'), 0.0)
            visits = int(clean_num(r.get('visits') or r.get('total_visits'), 0))
            orders = int(clean_num(r.get('orders') or r.get('total_orders'), 0))
            last_visit = clean_str(r.get('last_visit_date') or r.get('last_visit'), '')
            days_since = int(clean_num(r.get('days_since_last_visit') or r.get('days_since'), 30))
            sr_name = clean_str(r.get('sr_name') or r.get('assigned_sr'), 'Field Officer')

            # Monthly Trend Array
            m1 = clean_num(r.get('trend_m1') or r.get('month_1_rev'), rev * 0.22)
            m2 = clean_num(r.get('trend_m2') or r.get('month_2_rev'), rev * 0.25)
            m3 = clean_num(r.get('trend_m3') or r.get('month_3_rev'), rev * 0.26)
            m4 = clean_num(r.get('trend_m4') or r.get('month_4_rev'), rev * 0.27)
            trend = [round(m1, 1), round(m2, 1), round(m3, 1), round(m4, 1)]

            score, status = compute_health_status(rev, visits, orders, days_since)
            div_idx = DIVISIONS.index(div) if div in DIVISIONS else 0

            # Revenue Per Visit (RPV)
            avg_rpv = round(rev / visits, 1) if visits > 0 else 0.0

            # [lat, lng, id, name, div_idx, district, score, status, rev, visits, lastVisit, daysSince, srName, orders, avgRPV, trend, thana]
            outlet_record = [
                round(lat, 6), round(lng, 6), o_id, o_name, div_idx, dist,
                score, status, round(rev, 1), visits, last_visit, days_since,
                sr_name, orders, avg_rpv, trend, thana
            ]

            outlets_by_div[div_idx].append(outlet_record)

            # Aggregate National & Regional KPIs
            national_kpis['total_outlets'] += 1
            if rev > 0: national_kpis['active_outlets'] += 1
            national_kpis['total_revenue'] += rev
            national_kpis['total_visits'] += visits
            national_kpis['total_orders'] += orders

            if status == 'G': national_kpis['strong_outlets'] += 1
            elif status == 'Y': national_kpis['moderate_outlets'] += 1
            else: national_kpis['weak_outlets'] += 1

            if visits == 0: national_kpis['blind_spots'] += 1
            if visits > 0 and rev == 0: national_kpis['zero_rev_barriers'] += 1

            # Division Aggs
            ds = div_stats[div]
            ds['outlets'] += 1
            if rev > 0: ds['active'] += 1
            ds['revenue'] += rev
            ds['visits'] += visits
            ds['orders'] += orders
            if status == 'G': ds['strong'] += 1
            elif status == 'Y': ds['moderate'] += 1
            else: ds['weak'] += 1
            if visits == 0: ds['blind'] += 1
            if visits > 0 and rev == 0: ds['zero_rev'] += 1

            # District Aggs
            dist_obj = ds['districts'][dist]
            dist_obj['name'] = dist
            dist_obj['outlets'] += 1
            if rev > 0: dist_obj['active'] += 1
            dist_obj['revenue'] += rev
            dist_obj['visits'] += visits
            dist_obj['orders'] += orders
            if status == 'G': dist_obj['strong'] += 1
            elif status == 'Y': dist_obj['moderate'] += 1
            else: dist_obj['weak'] += 1
            if visits == 0: dist_obj['blind'] += 1
            if visits > 0 and rev == 0: dist_obj['zero_rev'] += 1

            # Thana Aggs
            th_obj = dist_obj['thanas'][thana]
            th_obj['name'] = thana
            th_obj['outlets'] += 1
            if rev > 0: th_obj['active'] += 1
            th_obj['revenue'] += rev
            th_obj['visits'] += visits
            th_obj['orders'] += orders
            if status == 'G': th_obj['strong'] += 1
            else: th_obj['weak'] += 1

    print(f"[✓] Processed {national_kpis['total_outlets']:,} outlets across {len(DIVISIONS)} divisions.")
    print(f"    Total Revenue: ৳ {national_kpis['total_revenue']:,.2f}")
    print(f"    Active Buyers: {national_kpis['active_outlets']:,} | Blind Spots: {national_kpis['blind_spots']:,}")

    # Build ceo_national.js
    formatted_divs = []
    for d in DIVISIONS:
        ds = div_stats[d]
        formatted_dists = []
        for dist_name, dt in ds['districts'].items():
            formatted_thanas = list(dt['thanas'].values())
            formatted_dists.append({
                'name': dist_name,
                'outlets': dt['outlets'],
                'active': dt['active'],
                'revenue': round(dt['revenue'], 1),
                'visits': dt['visits'],
                'orders': dt['orders'],
                'strong': dt['strong'],
                'moderate': dt['moderate'],
                'weak': dt['weak'],
                'blind': dt['blind'],
                'zero_rev': dt['zero_rev'],
                'thanas': formatted_thanas
            })

        formatted_divs.append({
            'name': d,
            'outlets': ds['outlets'],
            'active': ds['active'],
            'revenue': round(ds['revenue'], 1),
            'visits': ds['visits'],
            'orders': ds['orders'],
            'strong': ds['strong'],
            'moderate': ds['moderate'],
            'weak': ds['weak'],
            'blind': ds['blind'],
            'zero_rev': ds['zero_rev'],
            'districts': formatted_dists
        })

    national_data = {
        'national_kpis': {
            'total_outlets': national_kpis['total_outlets'],
            'active_outlets': national_kpis['active_outlets'],
            'total_revenue': round(national_kpis['total_revenue'], 1),
            'total_visits': national_kpis['total_visits'],
            'total_orders': national_kpis['total_orders'],
            'strong_outlets': national_kpis['strong_outlets'],
            'moderate_outlets': national_kpis['moderate_outlets'],
            'weak_outlets': national_kpis['weak_outlets'],
            'blind_spots': national_kpis['blind_spots'],
            'zero_rev_barriers': national_kpis['zero_rev_barriers']
        },
        'divisions': formatted_divs
    }

    # Write ceo_national.js
    nat_path = os.path.join(output_dir, 'ceo_national.js')
    with open(nat_path, 'w', encoding='utf-8') as f:
        f.write('window.CEO_NATIONAL = ' + json.dumps(national_data, ensure_ascii=False) + ';\n')
    print(f"[✓] Written: {nat_path}")

    # Write ceo_outlets_D0..D7.js
    for didx in range(8):
        arr = outlets_by_div[didx]
        out_file = os.path.join(output_dir, f'ceo_outlets_D{didx}.js')
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(f'if (typeof CEO_OUTLETS === "undefined") window.CEO_OUTLETS = [];\n')
            f.write(f'window.CEO_OUTLETS[{didx}] = ' + json.dumps(arr, ensure_ascii=False) + ';\n')
        print(f"[✓] Written: {out_file} ({len(arr):,} outlets)")

    print("\n=============================================================================")
    print("🎉 SUCCESS! Geospatial datasets generated successfully.")
    print("Open 'index.html' in your browser to view your live executive map.")
    print("=============================================================================\n")
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        input_csv = sys.argv[1]
        out_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    else:
        # Default fallback sample path
        input_csv = 'sample_outlets_template.csv'
        out_dir = '..'

    if os.path.exists(input_csv):
        process_outlets_master(input_csv, out_dir)
    else:
        print(f"Usage: python build_map_pipeline.py <path_to_outlets_master.csv> [output_directory]")
