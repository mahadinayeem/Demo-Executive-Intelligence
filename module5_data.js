window.MODULE5_DATA = {
  "summary": {
    "total_revenue": 4625339619.3,
    "total_orders": 3508543,
    "total_visits": 1569940,
    "active_srs": 965,
    "model_r2_score": 0.884,
    "causal_architecture": "Two-Stage Structural Equation Model (SEM) \u2014 Pure Controllable Inputs -> Behavioral Yield -> Revenue (BDT)",
    "forecast_growth_rate": "+18.4% Annualized"
  },
  "feature_importance": [
    {
      "key": "dwell_time",
      "name": "Shop Dwell Time (Mins)",
      "bengali_name": "\u09a6\u09cb\u0995\u09be\u09a8\u09c7 \u0995\u09be\u099f\u09be\u09a8\u09cb \u0995\u09cb\u09df\u09be\u09b2\u09bf\u099f\u09bf \u09b8\u09ae\u09df (\u09ae\u09bf\u09a8\u09bf\u099f)",
      "type": "Pure Controllable Input",
      "desc": "Physical face-to-face pitch & relationship time spent per visited outlet",
      "importance_pct": 36.8,
      "elasticity": 1.54,
      "category": "Pitch Quality & Relationship",
      "mechanism_bn": "\u09a6\u09cb\u0995\u09be\u09a8\u09c7 \u09aa\u09b0\u09cd\u09af\u09be\u09aa\u09cd\u09a4 \u09b8\u09ae\u09df \u09a6\u09bf\u09b2\u09c7 \u09b0\u09bf\u099f\u09c7\u0987\u09b2\u09be\u09b0 \u09b8\u09cd\u099f\u0995 \u099a\u09c7\u0995 \u0993 \u09aa\u09c2\u09b0\u09cd\u09a3\u09be\u0999\u09cd\u0997 \u09aa\u09cb\u09b0\u09cd\u099f\u09ab\u09cb\u09b2\u09bf\u0993 \u09aa\u09bf\u099a \u0995\u09b0\u09be\u09b0 \u09b8\u09c1\u09af\u09cb\u0997 \u09aa\u09be\u0993\u09df\u09be \u09af\u09be\u09df\u0964"
    },
    {
      "key": "pitch_depth",
      "name": "Pitch Depth (SKU Lines Offered)",
      "bengali_name": "\u09aa\u09bf\u099a \u09a1\u09c7\u09aa\u09a5 (\u0995\u09df\u099f\u09bf \u09aa\u09cd\u09b0\u09cb\u09a1\u09be\u0995\u09cd\u099f \u0995\u09cd\u09af\u09be\u099f\u09be\u0997\u09b0\u09bf \u0985\u09ab\u09be\u09b0 \u0995\u09b0\u09be \u09b9\u09df\u09c7\u099b\u09c7)",
      "type": "Pure Controllable Input",
      "desc": "Active presentation of multi-tier tea lines & complementary products during sales call",
      "importance_pct": 26.4,
      "elasticity": 1.48,
      "category": "Portfolio Presentation",
      "mechanism_bn": "\u09b6\u09c1\u09a7\u09c1 \u09e7\u099f\u09bf \u09b0\u09c1\u099f\u09bf\u09a8 \u099a\u09be \u0985\u09ab\u09be\u09b0 \u09a8\u09be \u0995\u09b0\u09c7 \u09aa\u09cd\u09b0\u09bf\u09ae\u09bf\u09df\u09be\u09ae \u09ac\u09cd\u09b2\u09c7\u09a8\u09cd\u09a1 \u0993 \u09ab\u09cd\u09af\u09be\u09ae\u09bf\u09b2\u09bf \u09aa\u09cd\u09af\u09be\u0995 \u098f\u0995\u09b8\u09be\u09a5\u09c7 \u0985\u09ab\u09be\u09b0 \u0995\u09b0\u09be\u0964"
    },
    {
      "key": "time_of_day_window",
      "name": "Optimal Time-of-Day Execution (%)",
      "bengali_name": "\u09aa\u09bf\u0995 \u0986\u0993\u09df\u09be\u09b0 \u099f\u09cd\u09b0\u09c7\u09a1\u09bf\u0982 \u0989\u0987\u09a8\u09cd\u09a1\u09cb \u09ac\u09cd\u09af\u09ac\u09b9\u09be\u09b0 (\u09b8\u0995\u09be\u09b2 \u09ee:\u09e9\u09e6-\u09e7\u09e7:\u09e9\u09e6)",
      "type": "Pure Controllable Input",
      "desc": "Executing sales calls during prime trading hours when retailers are ready to re-order",
      "importance_pct": 18.2,
      "elasticity": 1.22,
      "category": "Timing & Schedule",
      "mechanism_bn": "\u09a6\u09c1\u09aa\u09c1\u09b0\u09c7\u09b0 \u0985\u09b2\u09b8 \u09b8\u09ae\u09df\u09c7\u09b0 \u099a\u09c7\u09df\u09c7 \u09b8\u0995\u09be\u09b2\u09c7\u09b0 \u09aa\u09bf\u0995 \u09ac\u09c7\u099a\u09be\u0995\u09c7\u09a8\u09be\u09b0 \u09b8\u09ae\u09df \u09b0\u09bf\u099f\u09c7\u0987\u09b2\u09be\u09b0\u09c7\u09b0 \u0995\u09be\u099b\u09c7 \u09aa\u09cc\u0981\u099b\u09be\u09a8\u09cb\u0964"
    },
    {
      "key": "route_transit_lag",
      "name": "Route Transit Compactness (Min/Lag)",
      "bengali_name": "\u0995\u09cd\u09b2\u09be\u09b8\u09cd\u099f\u09be\u09b0 \u09ac\u09bf\u099f \u0993 \u099f\u09cd\u09b0\u09be\u09ad\u09c7\u09b2 \u099f\u09be\u0987\u09ae \u0985\u09aa\u099f\u09bf\u09ae\u09be\u0987\u099c\u09c7\u09b6\u09a8",
      "type": "Pure Controllable Input",
      "desc": "Minimizing inter-store dead transit time through geographically dense cluster beats",
      "importance_pct": 11.6,
      "elasticity": 0.95,
      "category": "Route Routing & Logistics",
      "mechanism_bn": "\u09a6\u09cb\u0995\u09be\u09a8 \u09a5\u09c7\u0995\u09c7 \u09a6\u09cb\u0995\u09be\u09a8\u09c7\u09b0 \u0985\u09aa\u09cd\u09b0\u09df\u09cb\u099c\u09a8\u09c0\u09df \u09a6\u09c2\u09b0\u09a4\u09cd\u09ac \u0993 \u099f\u09cd\u09b0\u09be\u09a8\u099c\u09bf\u099f \u09b8\u09ae\u09df \u0995\u09ae\u09bf\u09df\u09c7 \u09b9\u09be\u0981\u099f\u09be \u0995\u09cd\u09b2\u09be\u09b8\u09cd\u099f\u09be\u09b0 \u09ac\u09bf\u099f \u09a8\u09bf\u09b6\u09cd\u099a\u09bf\u09a4 \u0995\u09b0\u09be\u0964"
    },
    {
      "key": "beat_regularity",
      "name": "Beat Cadence & Cycle Regularity",
      "bengali_name": "\u09ad\u09bf\u099c\u09bf\u099f \u09b8\u09be\u0987\u0995\u09c7\u09b2 \u09a8\u09bf\u09df\u09ae\u09bf\u09a4\u0995\u09b0\u09a3 (PJP \u09a1\u09bf\u09b8\u09bf\u09aa\u09cd\u09b2\u09bf\u09a8)",
      "type": "Pure Controllable Input",
      "desc": "Punctual, predictable beat rhythm ensuring retailers never face stock-outs",
      "importance_pct": 7.0,
      "elasticity": 0.72,
      "category": "Beat Rhythm & Cadence",
      "mechanism_bn": "\u09a8\u09bf\u09b0\u09cd\u09a6\u09bf\u09b7\u09cd\u099f \u09ac\u09be\u09b0\u09c7 \u09a8\u09bf\u09df\u09ae\u09bf\u09a4 \u09a6\u09cb\u0995\u09be\u09a8\u09c7 \u09af\u09be\u0993\u09df\u09be, \u09af\u09be\u09a4\u09c7 \u09b0\u09bf\u099f\u09c7\u0987\u09b2\u09be\u09b0 \u0985\u09a8\u09cd\u09af \u09ac\u09cd\u09b0\u09cd\u09af\u09be\u09a8\u09cd\u09a1\u09c7\u09b0 \u0995\u09be\u099b\u09c7 \u09b8\u09cd\u099f\u0995 \u09a8\u09be \u0995\u09c7\u09a8\u09c7\u0964"
    }
  ],
  "pdp_insights": {
    "dwell_time": [
      {
        "x": 1,
        "label": "1 min",
        "rev_index": 32,
        "marginal_uplift": "+0%",
        "status": "Sub-threshold (Rushed Visit)"
      },
      {
        "x": 3,
        "label": "3 mins",
        "rev_index": 45,
        "marginal_uplift": "+22%",
        "status": "Sub-threshold (Surface Check)"
      },
      {
        "x": 5,
        "label": "5 mins",
        "rev_index": 68,
        "marginal_uplift": "+45%",
        "status": "Approaching Inflection"
      },
      {
        "x": 8,
        "label": "8 mins",
        "rev_index": 122,
        "marginal_uplift": "+69%",
        "status": "Golden Tipping Point (Optimal)"
      },
      {
        "x": 12,
        "label": "12 mins",
        "rev_index": 175,
        "marginal_uplift": "+43%",
        "status": "Deep Basket Pitch Zone"
      },
      {
        "x": 16,
        "label": "16 mins",
        "rev_index": 212,
        "marginal_uplift": "+21%",
        "status": "Relationship Building"
      },
      {
        "x": 20,
        "label": "20 mins",
        "rev_index": 228,
        "marginal_uplift": "+7%",
        "status": "Diminishing Returns Zone"
      },
      {
        "x": 25,
        "label": "25 mins",
        "rev_index": 234,
        "marginal_uplift": "+2%",
        "status": "Plateaued / Time Cannibalization"
      }
    ],
    "time_of_day": [
      {
        "x": 8,
        "label": "08:00 AM",
        "rev_index": 85,
        "marginal_uplift": "+35%",
        "status": "Store Opening & Stock Check"
      },
      {
        "x": 9,
        "label": "09:00 AM",
        "rev_index": 145,
        "marginal_uplift": "+70%",
        "status": "Golden Trading Hour #1"
      },
      {
        "x": 10,
        "label": "10:00 AM",
        "rev_index": 180,
        "marginal_uplift": "+24%",
        "status": "Golden Trading Hour #2 (Peak)"
      },
      {
        "x": 11,
        "label": "11:00 AM",
        "rev_index": 160,
        "marginal_uplift": "-11%",
        "status": "High Conversion Window"
      },
      {
        "x": 12,
        "label": "12:00 PM",
        "rev_index": 115,
        "marginal_uplift": "-28%",
        "status": "Midday Transition"
      },
      {
        "x": 14,
        "label": "02:00 PM",
        "rev_index": 65,
        "marginal_uplift": "-43%",
        "status": "Afternoon Slump / Low Re-order"
      },
      {
        "x": 16,
        "label": "04:00 PM",
        "rev_index": 110,
        "marginal_uplift": "+69%",
        "status": "Evening Tea Stall Rush"
      },
      {
        "x": 18,
        "label": "06:00 PM",
        "rev_index": 92,
        "marginal_uplift": "-16%",
        "status": "Late Beat Wrap-up"
      }
    ],
    "pitch_depth": [
      {
        "x": 1.0,
        "label": "1.0 SKU (Single Item)",
        "rev_index": 30,
        "marginal_uplift": "+0%",
        "status": "Commodity Order Only"
      },
      {
        "x": 2.0,
        "label": "2.0 SKUs",
        "rev_index": 65,
        "marginal_uplift": "+116%",
        "status": "Core Volume + Secondary Line"
      },
      {
        "x": 3.5,
        "label": "3.5 SKUs",
        "rev_index": 152,
        "marginal_uplift": "+133%",
        "status": "Cross-Category Inflection Threshold"
      },
      {
        "x": 5.0,
        "label": "5.0 SKUs",
        "rev_index": 235,
        "marginal_uplift": "+54%",
        "status": "High Margin Multi-Basket"
      },
      {
        "x": 6.5,
        "label": "6.5 SKUs",
        "rev_index": 280,
        "marginal_uplift": "+19%",
        "status": "Comprehensive Portfolio Saturation"
      },
      {
        "x": 8.0,
        "label": "8.0 SKUs",
        "rev_index": 298,
        "marginal_uplift": "+6%",
        "status": "Wholesale Capacity Ceiling"
      }
    ],
    "transit_lag": [
      {
        "x": 2,
        "label": "2 mins (Dense Walk)",
        "capacity_calls": 42,
        "efficiency_pct": 98,
        "status": "Optimal Urban Beat"
      },
      {
        "x": 5,
        "label": "5 mins (Market Cluster)",
        "capacity_calls": 34,
        "efficiency_pct": 88,
        "status": "Bazar Cluster Walk"
      },
      {
        "x": 8,
        "label": "8 mins (Semi-Urban)",
        "capacity_calls": 27,
        "efficiency_pct": 74,
        "status": "Sub-optimal Transit Drag"
      },
      {
        "x": 12,
        "label": "12 mins (Feeder Jumps)",
        "capacity_calls": 21,
        "efficiency_pct": 58,
        "status": "Inter-Village Transition"
      },
      {
        "x": 18,
        "label": "18 mins (Rural Road)",
        "capacity_calls": 16,
        "efficiency_pct": 42,
        "status": "Severe Mileage Dead-Time"
      },
      {
        "x": 25,
        "label": "25 mins (Scattered)",
        "capacity_calls": 12,
        "efficiency_pct": 29,
        "status": "High Fatigue / Low Dwell"
      }
    ]
  },
  "regional_kpi_calibration": [
    {
      "archetype": "Urban Core / Metro (Dhaka / Chittagong)",
      "territory_count": 118,
      "sr_count": 324,
      "current_revenue": 1985420000.0,
      "transit_lag_min": 3.2,
      "target_transit_lag": 2.5,
      "current_dwell_time": 6.2,
      "target_dwell_time": 8.5,
      "current_pitch_depth": 2.8,
      "target_pitch_depth": 4.5,
      "morning_slot_pct": 48.0,
      "target_morning_slot_pct": 65.0,
      "current_calls_day": 26.5,
      "target_calls_day": 38.0,
      "resulting_strike_rate": "62% -> 74%",
      "growth_potential_pct": 24.5,
      "strategic_focus": "Micro-Walking Routes inside high-density alleys; pitch premium jars and specialty blends in morning peak."
    },
    {
      "archetype": "Cluster Market / Semi-Urban (Gazipur, Narayanganj, Upazila Bazars)",
      "territory_count": 186,
      "sr_count": 382,
      "current_revenue": 1652180000.0,
      "transit_lag_min": 7.5,
      "target_transit_lag": 5.0,
      "current_dwell_time": 7.5,
      "target_dwell_time": 10.0,
      "current_pitch_depth": 2.4,
      "target_pitch_depth": 3.8,
      "morning_slot_pct": 42.0,
      "target_morning_slot_pct": 60.0,
      "current_calls_day": 22.0,
      "target_calls_day": 28.0,
      "resulting_strike_rate": "54% -> 68%",
      "growth_potential_pct": 28.2,
      "strategic_focus": "Anchor Bazar cluster locking; lock core tea volume with grocers and drive medium packet distribution."
    },
    {
      "archetype": "Rural & Deep Upazila Feeders (Village Hats & Remote Feeders)",
      "territory_count": 238,
      "sr_count": 260,
      "current_revenue": 987739619.3,
      "transit_lag_min": 17.5,
      "target_transit_lag": 12.0,
      "current_dwell_time": 9.0,
      "target_dwell_time": 13.0,
      "current_pitch_depth": 2.1,
      "target_pitch_depth": 3.2,
      "morning_slot_pct": 35.0,
      "target_morning_slot_pct": 55.0,
      "current_calls_day": 16.5,
      "target_calls_day": 22.0,
      "resulting_strike_rate": "48% -> 60%",
      "growth_potential_pct": 32.8,
      "strategic_focus": "Bi-weekly cluster beat cycle; eliminate daily random travel, focus on high-ticket weekly tea replenishment."
    }
  ],
  "uplift_scenarios": [
    {
      "input_lever": "Shop Dwell Time (+2 / +4 / +6 mins)",
      "bengali_lever": "\u09a6\u09cb\u0995\u09be\u09a8\u09c7 \u0985\u09ac\u09b8\u09cd\u09a5\u09be\u09a8\u09c7\u09b0 \u09b8\u09ae\u09df \u09ac\u09be\u09dc\u09be\u09a8\u09cb (+\u09e8 / +\u09ea / +\u09ec \u09ae\u09bf\u09a8\u09bf\u099f)",
      "elasticity": 1.54,
      "uplift_5pct": 356151150.69,
      "uplift_10pct": 712302301.37,
      "uplift_15pct": 1068453452.06,
      "action": "Mandate 8-10 min dwell standard; conduct shelf audit & active objection handling"
    },
    {
      "input_lever": "Pitch Depth (+0.5 / +1.0 / +1.5 SKUs)",
      "bengali_lever": "\u09aa\u09bf\u099a \u09a1\u09c7\u09aa\u09a5 \u09ac\u09be \u0985\u09ab\u09be\u09b0 \u0995\u09b0\u09be SKU \u09b8\u0982\u0996\u09cd\u09af\u09be \u09ac\u09be\u09dc\u09be\u09a8\u09cb",
      "elasticity": 1.48,
      "uplift_5pct": 342275131.83,
      "uplift_10pct": 684550263.66,
      "uplift_15pct": 1026825395.48,
      "action": "Bundle high-margin specialty blends with core tea volume using structured trade combo deals"
    },
    {
      "input_lever": "Morning Peak Window Execution (+10% / +20% / +30%)",
      "bengali_lever": "\u09b8\u0995\u09be\u09b2\u09c7\u09b0 \u0997\u09cb\u09b2\u09cd\u09a1\u09c7\u09a8 \u099f\u09cd\u09b0\u09c7\u09a1\u09bf\u0982 \u0986\u0993\u09df\u09be\u09b0\u09c7 \u09ad\u09bf\u099c\u09bf\u099f \u09ac\u09be\u09dc\u09be\u09a8\u09cb (\u09e6\u09ee:\u09e9\u09e6-\u09e7\u09e7:\u09e9\u09e6)",
      "elasticity": 1.22,
      "uplift_5pct": 282145716.78,
      "uplift_10pct": 564291433.55,
      "uplift_15pct": 846437150.33,
      "action": "Shift beat start time to 8:30 AM sharp; capture morning store restocking decisions"
    },
    {
      "input_lever": "Route Transit Compactness (-2 / -4 / -6 min Lag)",
      "bengali_lever": "\u0995\u09cd\u09b2\u09be\u09b8\u09cd\u099f\u09be\u09b0 \u09ac\u09bf\u099f\u09c7\u09b0 \u09ae\u09be\u09a7\u09cd\u09af\u09ae\u09c7 \u099f\u09cd\u09b0\u09be\u09ad\u09c7\u09b2 \u099f\u09be\u0987\u09ae \u0993 \u099f\u09cd\u09b0\u09be\u09a8\u099c\u09bf\u099f \u09b2\u09cd\u09af\u09be\u0997 \u0995\u09ae\u09be\u09a8\u09cb",
      "elasticity": 0.95,
      "uplift_5pct": 219703631.92,
      "uplift_10pct": 439407263.83,
      "uplift_15pct": 659110895.75,
      "action": "Implement GIS cluster beats to eliminate zigzag travel; convert travel time into in-store selling minutes"
    },
    {
      "input_lever": "Beat Regularity & Cadence Discipline (+5% / +10% / +15%)",
      "bengali_lever": "\u09a8\u09bf\u09b0\u09cd\u09a6\u09bf\u09b7\u09cd\u099f \u09ac\u09be\u09b0\u09c7 \u09a8\u09bf\u09df\u09ae\u09bf\u09a4 \u09a6\u09cb\u0995\u09be\u09a8\u09c7 \u09af\u09be\u0993\u09df\u09be\u09b0 \u09a1\u09bf\u09b8\u09bf\u09aa\u09cd\u09b2\u09bf\u09a8 (PJP)",
      "elasticity": 0.72,
      "uplift_5pct": 166512226.29,
      "uplift_10pct": 333024452.59,
      "uplift_15pct": 499536678.88,
      "action": "Strict PJP adherence tracking to protect accounts from competitor brand incursions"
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