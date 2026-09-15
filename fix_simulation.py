"""
Fix simulation data - compute meaningful cross-sell uplift
"""
import json

with open(r'e:\ITL FINAL ADV ANALYSIS\module2_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

# The issue: mega-outlets (tea stall distributors) with single HTS SKU dominate
# Better simulation: look at Bronze/Silver tier outlets
tiers = {t['tier']: t for t in d['tiers']}
bronze = tiers['Bronze']
silver = tiers['Silver']
gold = tiers['Gold']
plat = tiers['Platinum']

# Meaningful scenario: If Bronze outlets (1762 avg) reach Silver avg (5754)
# That's 3x uplift
bronze_outlets = bronze['outlet_count']
bronze_avg = bronze['avg_revenue']
silver_avg = silver['avg_revenue']
gold_avg = gold['avg_revenue']

uplift_bronze_to_silver = (silver_avg - bronze_avg) * bronze_outlets
uplift_silver_to_gold = (gold_avg - silver_avg) * silver['outlet_count']

# Also: SKU expansion rate - outlets with 1 SKU vs 2 SKU vs 3+
# From basket analysis: 46% of orders are multi-SKU
# If all single-SKU outlets added 1 cross-sell with avg basket lift of 2.1x...
sim_corrected = {
    'scenario_bronze_to_silver': {
        'outlets': bronze_outlets,
        'current_avg': round(bronze_avg, 0),
        'target_avg': round(silver_avg, 0),
        'uplift_total': round(uplift_bronze_to_silver, 0),
        'uplift_pct': round((silver_avg - bronze_avg) / bronze_avg * 100, 0)
    },
    'scenario_silver_to_gold': {
        'outlets': silver['outlet_count'],
        'current_avg': round(silver_avg, 0),
        'target_avg': round(gold_avg, 0),
        'uplift_total': round(uplift_silver_to_gold, 0),
        'uplift_pct': round((gold_avg - silver_avg) / silver_avg * 100, 0)
    },
    'basket_expansion': {
        'multi_item_orders_pct': d['simulation']['multi_item_orders_pct'],
        'single_sku_outlets': d['simulation']['single_sku_outlets'],
        'single_sku_pct': d['simulation']['single_sku_pct'],
        'cross_sell_target': 46.0,  # goal: bring all to 46% multi-item rate
        'current_rate': d['simulation']['multi_item_orders_pct']
    },
    'tier_upgrade_scenarios': [
        {'from':'Bronze','to':'Silver','outlets':bronze_outlets,'uplift':round(uplift_bronze_to_silver,0),'uplift_M':round(uplift_bronze_to_silver/1e6,1)},
        {'from':'Silver','to':'Gold','outlets':silver['outlet_count'],'uplift':round(uplift_silver_to_gold,0),'uplift_M':round(uplift_silver_to_gold/1e6,1)},
        {'from':'Bronze+Silver','to':'Gold','outlets':bronze_outlets+silver['outlet_count'],
         'uplift':round(uplift_bronze_to_silver+uplift_silver_to_gold,0),
         'uplift_M':round((uplift_bronze_to_silver+uplift_silver_to_gold)/1e6,1)},
    ],
    'total_opportunity_M': round((uplift_bronze_to_silver + uplift_silver_to_gold) / 1e6, 1)
}

d['simulation_v2'] = sim_corrected

with open(r'e:\ITL FINAL ADV ANALYSIS\module2_data.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

# Rewrite JS
with open(r'e:\ITL FINAL ADV ANALYSIS\module2_data.json', 'r', encoding='utf-8') as f:
    raw = f.read()
with open(r'e:\ITL FINAL ADV ANALYSIS\module2_data.js', 'w', encoding='utf-8') as f:
    f.write('const MODULE2_DATA = ')
    f.write(raw)
    f.write(';')

print('Simulation v2 written')
print(f'Bronze->Silver uplift: BDT {uplift_bronze_to_silver/1e6:.1f}M')
print(f'Silver->Gold uplift: BDT {uplift_silver_to_gold/1e6:.1f}M')
print(f'Total opportunity: BDT {(uplift_bronze_to_silver+uplift_silver_to_gold)/1e6:.1f}M')
