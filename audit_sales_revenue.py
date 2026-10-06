"""
Deep Dive Audit on Sales Revenue: Check Total Sum, Distributions, Top Outlets, and Outliers.
"""
import re, json, sys
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

rev_list = []
top_outlets = []

for didx in range(8):
    fpath = f'd:\\ITL FINAL ADV ANALYSIS\\ceo_outlets_D{didx}.js'
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    m = re.search(r'CEO_OUTLETS\[\d+\]\s*=\s*(\[.*\]);?', text, re.DOTALL)
    if m:
        arr = json.loads(m.group(1))
        for o in arr:
            rev = o[8] or 0
            rev_list.append(rev)
            if rev > 300000: # Over 3 Lakhs
                top_outlets.append({
                    'id': o[2],
                    'name': o[3],
                    'division': didx,
                    'district': o[5],
                    'thana': o[16] if len(o) > 16 else '',
                    'revenue': rev,
                    'visits': o[9] or 0,
                    'orders': o[13] or 0
                })

rev_arr = np.array(rev_list)
total_sum = np.sum(rev_arr)
total_outlets = len(rev_arr)
active_buyers = np.sum(rev_arr > 0)
zero_rev = np.sum(rev_arr == 0)

print(f"Total Outlets: {total_outlets:,}")
print(f"Active Buyers (Rev > 0): {active_buyers:,} ({active_buyers/total_outlets*100:.1f}%)")
print(f"Zero Revenue Outlets: {zero_rev:,} ({zero_rev/total_outlets*100:.1f}%)")
print(f"Total Sales Sum: BDT {total_sum:,.2f} ({total_sum/1e9:.3f} Billion BDT)")
print(f"Mean Revenue per Outlet: BDT {np.mean(rev_arr):,.2f}")
print(f"Mean Revenue among Active Buyers: BDT {np.mean(rev_arr[rev_arr>0]):,.2f}")
print(f"Median Revenue among Active: BDT {np.median(rev_arr[rev_arr>0]):,.2f}")
print(f"75th Percentile: BDT {np.percentile(rev_arr[rev_arr>0], 75):,.2f}")
print(f"90th Percentile: BDT {np.percentile(rev_arr[rev_arr>0], 90):,.2f}")
print(f"95th Percentile: BDT {np.percentile(rev_arr[rev_arr>0], 95):,.2f}")
print(f"99th Percentile: BDT {np.percentile(rev_arr[rev_arr>0], 99):,.2f}")
print(f"99.9th Percentile: BDT {np.percentile(rev_arr[rev_arr>0], 99.9):,.2f}")
print(f"Max Single Outlet Revenue: BDT {np.max(rev_arr):,.2f}")

top_outlets.sort(key=lambda x: x['revenue'], reverse=True)
print(f"\nTop 15 Outlets by 4-Month Revenue:")
for i, o in enumerate(top_outlets[:15]):
    print(f"{i+1}. ID: {o['id']} | {o['name']} ({o['district']} - {o['thana']}): BDT {o['revenue']:,.2f} | Orders: {o['orders']} | Visits: {o['visits']}")

# Check distribution of revenue tiers
print(f"\nRevenue Tiers Distribution:")
t_0 = np.sum(rev_arr == 0)
t_1_5k = np.sum((rev_arr > 0) & (rev_arr <= 5000))
t_5_20k = np.sum((rev_arr > 5000) & (rev_arr <= 20000))
t_20_50k = np.sum((rev_arr > 20000) & (rev_arr <= 50000))
t_50_100k = np.sum((rev_arr > 50000) & (rev_arr <= 100000))
t_100k_plus = np.sum(rev_arr > 100000)

print(f"0 (Zero Rev): {t_0:,} ({t_0/total_outlets*100:.1f}%)")
print(f"1 - 5,000 BDT: {t_1_5k:,} ({t_1_5k/total_outlets*100:.1f}%) | Sum: BDT {np.sum(rev_arr[(rev_arr>0)&(rev_arr<=5000)]):,.0f}")
print(f"5,000 - 20,000 BDT: {t_5_20k:,} ({t_5_20k/total_outlets*100:.1f}%) | Sum: BDT {np.sum(rev_arr[(rev_arr>5000)&(rev_arr<=20000)]):,.0f}")
print(f"20,000 - 50,000 BDT: {t_20_50k:,} ({t_20_50k/total_outlets*100:.1f}%) | Sum: BDT {np.sum(rev_arr[(rev_arr>20000)&(rev_arr<=50000)]):,.0f}")
print(f"50,000 - 100,000 BDT: {t_50_100k:,} ({t_50_100k/total_outlets*100:.1f}%) | Sum: BDT {np.sum(rev_arr[(rev_arr>50000)&(rev_arr<=100000)]):,.0f}")
print(f"100,000+ BDT (Key/Wholesale Accounts): {t_100k_plus:,} ({t_100k_plus/total_outlets*100:.1f}%) | Sum: BDT {np.sum(rev_arr[rev_arr>100000]):,.0f}")
