window.MODULE5_DATA = {
  "summary": {
    "total_revenue": 4625339619.3,
    "total_orders": 3508543,
    "total_visits": 1569940,
    "active_srs": 965,
    "model_r2_score": 0.884,
    "forecast_growth_rate": "+18.4% Annualized"
  },
  "feature_importance": [
    {
      "key": "strike_rate",
      "name": "Strike Rate (%)",
      "desc": "Effective order closing % on visited retailers",
      "importance_pct": 34.2,
      "elasticity": 1.85,
      "category": "Sales Effectiveness"
    },
    {
      "key": "sku_per_memo",
      "name": "SKU Breadth per Memo",
      "desc": "Multi-category basket building during pitch",
      "importance_pct": 24.8,
      "elasticity": 1.62,
      "category": "Basket Building"
    },
    {
      "key": "avg_duration",
      "name": "Visit Duration (Mins)",
      "desc": "Time spent in retail relationship & merchandise check",
      "importance_pct": 18.5,
      "elasticity": 1.34,
      "category": "Visit Quality"
    },
    {
      "key": "calls_per_day",
      "name": "Daily Call Productivity",
      "desc": "Number of physical GPS verified retail visits per day",
      "importance_pct": 12.6,
      "elasticity": 1.15,
      "category": "Work Rate"
    },
    {
      "key": "outlet_coverage",
      "name": "Active Outlet Universe",
      "desc": "Number of unique mapped doors covered per cycle",
      "importance_pct": 6.4,
      "elasticity": 0.85,
      "category": "Reach"
    },
    {
      "key": "working_days",
      "name": "Field Route Discipline",
      "desc": "Consistency of field deployment across monthly cycle",
      "importance_pct": 3.5,
      "elasticity": 0.6,
      "category": "Discipline"
    }
  ],
  "pdp_insights": {
    "visit_duration": [
      {
        "x": 1,
        "label": "1 min",
        "rev_index": 38,
        "marginal_uplift": "+0%",
        "status": "Sub-threshold (Superficial)"
      },
      {
        "x": 3,
        "label": "3 mins",
        "rev_index": 48,
        "marginal_uplift": "+26%",
        "status": "Sub-threshold"
      },
      {
        "x": 5,
        "label": "5 mins",
        "rev_index": 68,
        "marginal_uplift": "+42%",
        "status": "Approaching Inflection"
      },
      {
        "x": 8,
        "label": "8 mins",
        "rev_index": 115,
        "marginal_uplift": "+69%",
        "status": "Golden Tipping Point"
      },
      {
        "x": 12,
        "label": "12 mins",
        "rev_index": 168,
        "marginal_uplift": "+46%",
        "status": "High Yield Zone"
      },
      {
        "x": 16,
        "label": "16 mins",
        "rev_index": 210,
        "marginal_uplift": "+25%",
        "status": "Deep Engagement"
      },
      {
        "x": 20,
        "label": "20 mins",
        "rev_index": 228,
        "marginal_uplift": "+8%",
        "status": "Diminishing Returns"
      },
      {
        "x": 25,
        "label": "25 mins",
        "rev_index": 235,
        "marginal_uplift": "+3%",
        "status": "Plateaued"
      }
    ],
    "strike_rate": [
      {
        "x": 10,
        "label": "10%",
        "rev_index": 22,
        "marginal_uplift": "+0%",
        "status": "Severe Drag"
      },
      {
        "x": 25,
        "label": "25%",
        "rev_index": 45,
        "marginal_uplift": "+104%",
        "status": "Below Par"
      },
      {
        "x": 40,
        "label": "40%",
        "rev_index": 88,
        "marginal_uplift": "+95%",
        "status": "Approaching Benchmark"
      },
      {
        "x": 55,
        "label": "55%",
        "rev_index": 155,
        "marginal_uplift": "+76%",
        "status": "Exponential Inflection"
      },
      {
        "x": 70,
        "label": "70%",
        "rev_index": 220,
        "marginal_uplift": "+42%",
        "status": "Star Performer Band"
      },
      {
        "x": 85,
        "label": "85%",
        "rev_index": 265,
        "marginal_uplift": "+20%",
        "status": "Elite Closer"
      },
      {
        "x": 95,
        "label": "95%",
        "rev_index": 282,
        "marginal_uplift": "+6%",
        "status": "Near Ceiling"
      }
    ],
    "sku_per_memo": [
      {
        "x": 1.0,
        "label": "1.0 SKU",
        "rev_index": 30,
        "marginal_uplift": "+0%",
        "status": "Single-Item Order"
      },
      {
        "x": 2.0,
        "label": "2.0 SKUs",
        "rev_index": 62,
        "marginal_uplift": "+106%",
        "status": "Core Volume Only"
      },
      {
        "x": 3.5,
        "label": "3.5 SKUs",
        "rev_index": 142,
        "marginal_uplift": "+129%",
        "status": "Basket Multiplier Threshold"
      },
      {
        "x": 5.0,
        "label": "5.0 SKUs",
        "rev_index": 225,
        "marginal_uplift": "+58%",
        "status": "High Margin Multi-Category"
      },
      {
        "x": 6.5,
        "label": "6.5 SKUs",
        "rev_index": 275,
        "marginal_uplift": "+22%",
        "status": "Optimal Full-Portfolio"
      },
      {
        "x": 8.0,
        "label": "8.0 SKUs",
        "rev_index": 295,
        "marginal_uplift": "+7%",
        "status": "Wholesale Ceiling"
      }
    ]
  },
  "regional_kpi_calibration": [
    {
      "archetype": "Metro Tier-1 (Dhaka / Chittagong Core)",
      "territory_count": 118,
      "sr_count": 324,
      "current_revenue": 1985420000.0,
      "current_calls_day": 26.5,
      "target_calls_day": 28.0,
      "current_strike_rate": 62.4,
      "target_strike_rate": 72.0,
      "current_avg_duration": 6.2,
      "target_avg_duration": 9.5,
      "current_sku_memo": 2.8,
      "target_sku_memo": 4.2,
      "current_aov": 1850.0,
      "target_aov": 2400.0,
      "growth_potential_pct": 24.5,
      "strategic_focus": "Drive SKU Breadth & Premium Line Placement in high-traffic outlets."
    },
    {
      "archetype": "Semi-Urban / District HQs (Gazipur, Narayanganj, Sylhet)",
      "territory_count": 186,
      "sr_count": 382,
      "current_revenue": 1652180000.0,
      "current_calls_day": 22.0,
      "target_calls_day": 25.0,
      "current_strike_rate": 54.8,
      "target_strike_rate": 65.0,
      "current_avg_duration": 7.5,
      "target_avg_duration": 11.0,
      "current_sku_memo": 2.4,
      "target_sku_memo": 3.6,
      "current_aov": 1420.0,
      "target_aov": 1850.0,
      "growth_potential_pct": 28.2,
      "strategic_focus": "Balance call route density with structured trade schemes for mid-tier grocers."
    },
    {
      "archetype": "Rural & Deep Upazila Feeders",
      "territory_count": 238,
      "sr_count": 260,
      "current_revenue": 987739619.3,
      "current_calls_day": 16.5,
      "target_calls_day": 20.0,
      "current_strike_rate": 48.2,
      "target_strike_rate": 58.0,
      "current_avg_duration": 9.0,
      "target_avg_duration": 13.5,
      "current_sku_memo": 2.1,
      "target_sku_memo": 3.0,
      "current_aov": 1180.0,
      "target_aov": 1500.0,
      "growth_potential_pct": 32.8,
      "strategic_focus": "PJP Route optimization to reduce transit dead-time; focus on bulk weekly staples."
    }
  ],
  "uplift_scenarios": [
    {
      "kpi": "Strike Rate (+5% / +10% / +15%)",
      "elasticity": 1.85,
      "uplift_5pct": 427843914.79,
      "uplift_10pct": 855687829.57,
      "uplift_15pct": 1283531744.36,
      "action": "Deploy Objection Handling Scripts & Retail Re-order Reminders"
    },
    {
      "kpi": "SKU Breadth (+0.5 / +1.0 / +1.5 SKUs)",
      "elasticity": 1.62,
      "uplift_5pct": 374652509.16,
      "uplift_10pct": 749305018.33,
      "uplift_15pct": 1123957527.49,
      "action": "Bundle Complementary SKUs with Dealer Trade Incentives"
    },
    {
      "kpi": "Quality Visit Duration (+2 / +4 / +6 mins)",
      "elasticity": 1.34,
      "uplift_5pct": 309897754.49,
      "uplift_10pct": 619795508.99,
      "uplift_15pct": 929693263.48,
      "action": "Mandate Planogram Check & Merchandising Shelf Optimization"
    },
    {
      "kpi": "Call Productivity (+2 / +4 / +6 Calls/Day)",
      "elasticity": 1.15,
      "uplift_5pct": 265957028.11,
      "uplift_10pct": 531914056.22,
      "uplift_15pct": 797871084.33,
      "action": "Geographic Cluster Beat Optimization & Travel Time Reduction"
    }
  ],
  "sales_forecast": {
    "historical": [
      {
        "month": "2026-05",
        "revenue": 904942436.1,
        "orders": 664539,
        "type": "Historical"
      },
      {
        "month": "2026-06",
        "revenue": 1236376958.35,
        "orders": 954966,
        "type": "Historical"
      },
      {
        "month": "2026-07",
        "revenue": 1271175485.7,
        "orders": 950451,
        "type": "Historical"
      },
      {
        "month": "2026-08",
        "revenue": 1212844739.15,
        "orders": 938587,
        "type": "Historical"
      }
    ],
    "forecast": [
      {
        "month": "2026-08",
        "forecast_revenue": 1251655770.8,
        "ci_80_lower": 1195331261.11,
        "ci_80_upper": 1307980280.49,
        "ci_95_lower": 1145265030.28,
        "ci_95_upper": 1358046511.32,
        "type": "Forecast"
      },
      {
        "month": "2026-10",
        "forecast_revenue": 1395045455.91,
        "ci_80_lower": 1306265306.74,
        "ci_80_upper": 1483825605.08,
        "ci_95_lower": 1227349618.58,
        "ci_95_upper": 1562741293.24,
        "type": "Forecast"
      },
      {
        "month": "2026-10",
        "forecast_revenue": 1439686910.49,
        "ci_80_lower": 1327474421.07,
        "ci_80_upper": 1551899399.91,
        "ci_95_lower": 1227729986.03,
        "ci_95_upper": 1651643834.95,
        "type": "Forecast"
      },
      {
        "month": "2026-12",
        "forecast_revenue": 1485756891.63,
        "ci_80_lower": 1352038771.38,
        "ci_80_upper": 1619475011.88,
        "ci_95_lower": 1233178220.05,
        "ci_95_upper": 1738335563.21,
        "type": "Forecast"
      },
      {
        "month": "2026-12",
        "forecast_revenue": 1533301112.16,
        "ci_80_lower": 1379015663.91,
        "ci_80_upper": 1687586560.41,
        "ci_95_lower": 1241873043.23,
        "ci_95_upper": 1824729181.09,
        "type": "Forecast"
      },
      {
        "month": "2027-01",
        "forecast_revenue": 1377245132.3,
        "ci_80_lower": 1225435480.18,
        "ci_80_upper": 1529054784.42,
        "ci_95_lower": 1090493567.19,
        "ci_95_upper": 1663996697.41,
        "type": "Forecast"
      }
    ]
  }
};