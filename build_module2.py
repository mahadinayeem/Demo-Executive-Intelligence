"""
Module 2: Portfolio, SKU & Basket Blueprint — SmartPitch Advisor™
Generates all data needed for the Module 2 HTML dashboard.
"""
import csv, json, sys, math
from collections import defaultdict
from itertools import combinations

sys.stdout.reconfigure(encoding='utf-8')

print("=== MODULE 2 DATA BUILDER ===")
print("Loading orders...")

# ─── 1. LOAD ALL ORDERS ───────────────────────────────────────────────────────
products = {}          # sku -> {name, brand, cat}
order_items = defaultdict(set)   # order_id -> set of skus
outlet_orders = defaultdict(set) # buyer_code -> set of order_ids
sku_revenue = defaultdict(float)
sku_qty = defaultdict(float)
sku_orders = defaultdict(set)
sku_buyers = defaultdict(set)
brand_revenue = defaultdict(float)
cat_revenue = defaultdict(float)
outlet_revenue = defaultdict(float)
outlet_sku_set = defaultdict(set)   # buyer -> set of skus bought
monthly_revenue = defaultdict(float) # YYYY-MM -> revenue
territory_revenue = defaultdict(float)
territory_orders = defaultdict(set)

total_rows = 0
total_revenue = 0.0

with open(r'e:\ITL FINAL ADV ANALYSIS\itl_orders.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        total_rows += 1
        sku = r.get('product_sku', '')
        name = r.get('product_name', '')
        brand = r.get('product_brand_name', '')
        cat = r.get('product_category_name', '')
        amt = float(r.get('amount', '0') or 0)
        qty = float(r.get('order_qty', '0') or 0)
        oid = r.get('order_id', '')
        buyer = r.get('buyer_department_code', '')
        status = r.get('order_status', '')
        territory = r.get('seller_department_territory', '')
        created = r.get('created_at', '')[:7]  # YYYY-MM

        if status == 'cancelled':
            continue
            
        if amt > 500000:  # Threshold lowered to 5 Lakh BDT to catch all outliers
            continue

        if sku not in products:
            products[sku] = {'name': name, 'brand': brand, 'cat': cat}

        order_items[oid].add(sku)
        outlet_orders[buyer].add(oid)
        outlet_sku_set[buyer].add(sku)

        sku_revenue[sku] += amt
        sku_qty[sku] += qty
        sku_orders[sku].add(oid)
        sku_buyers[sku].add(buyer)
        brand_revenue[brand] += amt
        cat_revenue[cat] += amt
        outlet_revenue[buyer] += amt
        monthly_revenue[created] += amt
        territory_revenue[territory] += amt
        territory_orders[territory].add(oid)
        total_revenue += amt

print(f"Loaded {total_rows:,} rows | {len(order_items):,} orders | {len(products)} SKUs | {len(outlet_orders):,} outlets")

# ─── 2. PARETO ANALYSIS ───────────────────────────────────────────────────────
print("Computing Pareto...")
sku_list = []
for sku, rev in sku_revenue.items():
    p = products.get(sku, {})
    sku_list.append({
        'sku': sku,
        'name': p.get('name', ''),
        'brand': p.get('brand', ''),
        'category': p.get('cat', ''),
        'revenue': round(rev, 2),
        'qty': sku_qty[sku],
        'order_count': len(sku_orders[sku]),
        'buyer_count': len(sku_buyers[sku])
    })

sku_list.sort(key=lambda x: -x['revenue'])
total_rev = sum(s['revenue'] for s in sku_list)
cumulative = 0
for i, s in enumerate(sku_list):
    cumulative += s['revenue']
    s['revenue_share_pct'] = round(s['revenue'] / total_rev * 100, 2)
    s['cumulative_pct'] = round(cumulative / total_rev * 100, 2)
    s['rank'] = i + 1

# Top 20 for display
top20_skus = sku_list[:20]

# Category pareto
cat_list = sorted(cat_revenue.items(), key=lambda x: -x[1])
cat_total = sum(v for _, v in cat_list)
cat_cumulative = 0
cat_pareto = []
for cat, rev in cat_list:
    cat_cumulative += rev
    cat_pareto.append({
        'category': cat,
        'revenue': round(rev, 2),
        'share_pct': round(rev / cat_total * 100, 2),
        'cumulative_pct': round(cat_cumulative / cat_total * 100, 2)
    })

# Brand pareto
brand_list = sorted(brand_revenue.items(), key=lambda x: -x[1])
brand_total = sum(v for _, v in brand_list)
brand_cumulative = 0
brand_pareto = []
for brand, rev in brand_list[:20]:
    brand_cumulative += rev
    brand_pareto.append({
        'brand': brand,
        'revenue': round(rev, 2),
        'share_pct': round(rev / brand_total * 100, 2),
        'cumulative_pct': round(brand_cumulative / brand_total * 100, 2)
    })

# ─── 3. MARKET BASKET ANALYSIS ────────────────────────────────────────────────
print("Computing Market Basket Analysis (this takes a moment)...")

N_orders = len(order_items)  # total transactions

# Count individual item support
item_support = defaultdict(int)
for oid, skus in order_items.items():
    for sku in skus:
        item_support[sku] += 1

# Count pair co-occurrences (only for orders with 2+ items)
pair_count = defaultdict(int)
multi_item_orders = 0
for oid, skus in order_items.items():
    skus_list = sorted(skus)
    if len(skus_list) < 2:
        continue
    multi_item_orders += 1
    for a, b in combinations(skus_list, 2):
        pair_count[(a, b)] += 1

print(f"  Multi-item orders: {multi_item_orders:,} / {N_orders:,}")
print(f"  Unique pairs: {len(pair_count):,}")

# Compute Support, Confidence, Lift for top pairs
pair_metrics = []
min_support_count = 50  # minimum co-occurrences
for (a, b), co_count in pair_count.items():
    if co_count < min_support_count:
        continue
    support = co_count / N_orders
    conf_ab = co_count / item_support[a] if item_support[a] > 0 else 0
    conf_ba = co_count / item_support[b] if item_support[b] > 0 else 0
    lift = support / ((item_support[a] / N_orders) * (item_support[b] / N_orders)) if item_support[a] > 0 and item_support[b] > 0 else 0

    pname_a = products.get(a, {}).get('name', a)
    pname_b = products.get(b, {}).get('name', b)
    bname_a = products.get(a, {}).get('brand', '')
    bname_b = products.get(b, {}).get('brand', '')
    cat_a = products.get(a, {}).get('cat', '')
    cat_b = products.get(b, {}).get('cat', '')

    pair_metrics.append({
        'sku_a': a, 'name_a': pname_a, 'brand_a': bname_a, 'cat_a': cat_a,
        'sku_b': b, 'name_b': pname_b, 'brand_b': bname_b, 'cat_b': cat_b,
        'co_count': co_count,
        'support': round(support * 100, 4),
        'confidence_ab': round(conf_ab * 100, 2),
        'confidence_ba': round(conf_ba * 100, 2),
        'lift': round(lift, 3)
    })

pair_metrics.sort(key=lambda x: -x['lift'])
top_pairs = pair_metrics[:30]
print(f"  Top pairs by lift computed: {len(pair_metrics):,}")

# ─── 4. OUTLET SEGMENTATION (RFM-lite for SmartPitch) ────────────────────────
print("Computing outlet segmentation...")

# Compute outlet stats
outlet_stats = []
for buyer, oids in outlet_orders.items():
    if not buyer:
        continue
    rev = outlet_revenue.get(buyer, 0)
    n_orders = len(oids)
    n_skus = len(outlet_sku_set.get(buyer, set()))
    outlet_stats.append({
        'buyer': buyer,
        'revenue': round(rev, 2),
        'orders': n_orders,
        'sku_count': n_skus,
        'avg_order_value': round(rev / n_orders, 2) if n_orders > 0 else 0
    })

outlet_stats.sort(key=lambda x: -x['revenue'])
total_outlets = len(outlet_stats)

# Tier assignment (Quartiles)
n = len(outlet_stats)
for i, o in enumerate(outlet_stats):
    pct = (n - i) / n
    if pct >= 0.75:
        o['tier'] = 'Platinum'
    elif pct >= 0.50:
        o['tier'] = 'Gold'
    elif pct >= 0.25:
        o['tier'] = 'Silver'
    else:
        o['tier'] = 'Bronze'

tier_counts = defaultdict(int)
tier_revenue = defaultdict(float)
for o in outlet_stats:
    tier_counts[o['tier']] += 1
    tier_revenue[o['tier']] += o['revenue']

tier_summary = []
for t in ['Platinum', 'Gold', 'Silver', 'Bronze']:
    rev = tier_revenue[t]
    cnt = tier_counts[t]
    tier_summary.append({
        'tier': t,
        'outlet_count': cnt,
        'revenue': round(rev, 2),
        'revenue_share': round(rev / total_rev * 100, 2),
        'avg_revenue': round(rev / cnt, 2) if cnt > 0 else 0,
        'outlets': [o['buyer'] for o in outlet_stats if o['tier'] == t]
    })

# ─── 5. FINANCIAL SIMULATION ──────────────────────────────────────────────────
print("Computing financial simulation...")

# Revenue Concentration: Top N SKU contribution
concentration = {
    'top1': round(sku_list[0]['revenue'] / total_rev * 100, 1),
    'top3': round(sum(s['revenue'] for s in sku_list[:3]) / total_rev * 100, 1),
    'top5': round(sum(s['revenue'] for s in sku_list[:5]) / total_rev * 100, 1),
    'top10': round(sum(s['revenue'] for s in sku_list[:10]) / total_rev * 100, 1),
    'top20': round(sum(s['revenue'] for s in sku_list[:20]) / total_rev * 100, 1),
    'total_skus': len(sku_list),
    'total_revenue': round(total_rev, 2)
}

# Monthly trend (Exclude September as per user request due to incomplete data)
monthly_sorted = sorted(monthly_revenue.items())
monthly_trend = [{'month': m, 'revenue': round(v, 2)} for m, v in monthly_sorted if m and not m.endswith('-09')]

# Basket size distribution
basket_dist = defaultdict(int)
for oid, skus in order_items.items():
    sz = len(skus)
    if sz <= 10:
        basket_dist[sz] += 1
    else:
        basket_dist[10] += 1  # 10+

basket_distribution = [{'size': k, 'count': v} for k, v in sorted(basket_dist.items())]

# Cross-sell opportunity: outlets buying only 1 SKU (potential upsell targets)
single_sku_outlets = sum(1 for o in outlet_stats if o['sku_count'] == 1)
multi_sku_avg_rev = sum(o['revenue'] for o in outlet_stats if o['sku_count'] > 1) / max(1, sum(1 for o in outlet_stats if o['sku_count'] > 1))
single_sku_avg_rev = sum(o['revenue'] for o in outlet_stats if o['sku_count'] == 1) / max(1, single_sku_outlets)

simulation = {
    'single_sku_outlets': single_sku_outlets,
    'single_sku_pct': round(single_sku_outlets / total_outlets * 100, 1),
    'single_sku_avg_rev': round(single_sku_avg_rev, 2),
    'multi_sku_avg_rev': round(multi_sku_avg_rev, 2),
    'uplift_if_upsold': round((multi_sku_avg_rev - single_sku_avg_rev) * single_sku_outlets, 2),
    'total_outlets': total_outlets,
    'multi_item_orders_pct': round(multi_item_orders / N_orders * 100, 1)
}

avg_rev_bronze = next(t['avg_revenue'] for t in tier_summary if t['tier'] == 'Bronze')
avg_rev_silver = next(t['avg_revenue'] for t in tier_summary if t['tier'] == 'Silver')
avg_rev_gold = next(t['avg_revenue'] for t in tier_summary if t['tier'] == 'Gold')

cnt_bronze = next(t['outlet_count'] for t in tier_summary if t['tier'] == 'Bronze')
cnt_silver = next(t['outlet_count'] for t in tier_summary if t['tier'] == 'Silver')

b2s_uplift = (avg_rev_silver - avg_rev_bronze) * cnt_bronze
s2g_uplift = (avg_rev_gold - avg_rev_silver) * cnt_silver

simulation_v2 = {
    'total_opportunity_M': round((b2s_uplift + s2g_uplift) / 1000000, 1),
    'scenario_bronze_to_silver': {
        'outlets': cnt_bronze,
        'uplift_pct': round((avg_rev_silver - avg_rev_bronze) / max(1, avg_rev_bronze) * 100, 1) if avg_rev_bronze else 0,
        'uplift_total': round(b2s_uplift, 2)
    },
    'scenario_silver_to_gold': {
        'outlets': cnt_silver,
        'uplift_pct': round((avg_rev_gold - avg_rev_silver) / max(1, avg_rev_silver) * 100, 1) if avg_rev_silver else 0,
        'uplift_total': round(s2g_uplift, 2)
    }
}

# ─── 6. SMARTPITCH RULES ─────────────────────────────────────────────────────
print("Building SmartPitch rules...")

# For each tier, find best cross-sell SKU
# Rules: IF outlet buys SKU_A AND is in Tier X → PITCH SKU_B
# Use top pairs with high lift + high confidence
smartpitch_rules = []
seen_pairs = set()
for p in top_pairs[:15]:
    rule_key = (p['sku_a'], p['sku_b'])
    if rule_key in seen_pairs:
        continue
    seen_pairs.add(rule_key)
    smartpitch_rules.append({
        'trigger_sku': p['sku_a'],
        'trigger_name': p['name_a'][:35],
        'pitch_sku': p['sku_b'],
        'pitch_name': p['name_b'][:35],
        'confidence': p['confidence_ab'],
        'lift': p['lift'],
        'co_count': p['co_count'],
        'rationale': f"Stores buying {p['name_a'][:25]} also buy {p['name_b'][:25]} {p['confidence_ab']:.1f}% of time (Lift {p['lift']:.2f}x)"
    })

# ─── 7. PACKAGE OUTPUT ───────────────────────────────────────────────────────
print("Packaging output...")

module2_data = {
    'summary': {
        'total_rows': total_rows,
        'total_orders': len(order_items),
        'total_outlets': total_outlets,
        'total_skus': len(products),
        'total_revenue': round(total_rev, 2),
        'multi_item_order_pct': round(multi_item_orders / len(order_items) * 100, 1),
        'unique_pairs_analyzed': len(pair_metrics)
    },
    'pareto': {
        'sku': top20_skus,
        'category': cat_pareto,
        'brand': brand_pareto,
        'concentration': concentration
    },
    'basket': {
        'top_pairs': top_pairs,
        'basket_distribution': basket_distribution
    },
    'tiers': tier_summary,
    'simulation': simulation,
    'simulation_v2': simulation_v2,
    'smartpitch': smartpitch_rules,
    'monthly_trend': monthly_trend
}

with open(r'e:\ITL FINAL ADV ANALYSIS\module2_data.json', 'w', encoding='utf-8') as f:
    json.dump(module2_data, f, ensure_ascii=False, indent=2)

print("\n=== MODULE 2 DATA COMPLETE ===")
print(f"Total Revenue: BDT {total_rev/1e9:.2f}B")
print(f"Total Orders: {len(order_items):,}")
print(f"Total Outlets: {total_outlets:,}")
print(f"Top SKU: {sku_list[0]['name']} ({sku_list[0]['revenue_share_pct']}% of revenue)")
print(f"Top Pair by Lift: {top_pairs[0]['name_a'][:30]} + {top_pairs[0]['name_b'][:30]} (Lift={top_pairs[0]['lift']})")
print(f"Single-SKU Outlets: {simulation['single_sku_outlets']:,} ({simulation['single_sku_pct']}%)")
print(f"Potential Uplift: BDT {simulation['uplift_if_upsold']/1e6:.1f}M")
print("\nSaved: module2_data.json")
