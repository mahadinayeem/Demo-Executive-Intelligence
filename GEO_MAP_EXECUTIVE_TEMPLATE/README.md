# 🗺️ Executive Geospatial Map Engine (Universal Standalone Template)
> **A High-Performance, Enterprise-Grade 3-Tier Geospatial Intelligence Portal for Bangladesh FMCG & National Distribution Networks.**

---

## 🌟 Overview & Key Capabilities

This standalone template contains the complete, production-grade codebase for the **C-Suite Geospatial Executive Map** developed for national FMCG distribution analysis.

It is 100% self-contained, zero-dependency (runs directly in any modern web browser or web server), and designed to be effortlessly reused for **any company or dataset** across Bangladesh.

### ⚡ Core Architecture Highlights:
1. **3-Level Hierarchical Geo-Drilldown:**
   - **Level 1 (Nationwide):** 8 Division polygon heatmaps with aggregate revenue, door reach, and health breakdown.
   - **Level 2 (Division Drilldown):** 64 District boundaries with drilldown metrics and territory cards.
   - **Level 3 (District & Thana Drilldown):** Upazila/Thana boundaries with micro-clusters down to individual GPS retail stores.
2. **Canvas-Accelerated High-Density Pins & Spiderfy:**
   - Renders 200,000+ retail outlets smoothly at 60 FPS using dynamic Canvas and Leaflet MarkerCluster.
   - Features **Spiderfy auto-unpacking** for densely clustered street markets.
3. **9-Tier Composite Health & Gap Diagnostics:**
   - **Core Performers:** Diamond Core, Growth Engine, Steady Breadwinner, Low-Yield Frequent.
   - **At-Risk & Gaps:** High-Yield Declining, Dormant At-Risk, Fragile Buyer.
   - **Field Governance Gaps:** 
     - 🟠 **0-Visit Blind Spots:** Outlets receiving zero field visits.
     - 🔴 **0-Revenue Conversion Barriers:** Outlets visited frequently by sales reps but producing 0 sales.
4. **Interactive Modal Profile Cards:**
   - Click on any retail pin to view historical revenue, 4-month trend sparklines, visit frequency, Revenue Per Visit (RPV), and AI prescriptive action recommendations.
5. **Excel & PNG Export Engines:**
   - Real-time filtered CSV export with UTF-8 BOM encoding for seamless Microsoft Excel compatibility.
   - 1-click high-resolution PNG map screenshot exporter.

---

## 📁 Folder Structure

```text
GEO_MAP_EXECUTIVE_TEMPLATE/
│
├── index.html                  # Main executive map application (Clean standalone entry point)
├── ceo_national_map.html       # Backup copy of the main application
├── start_demo.bat              # 1-Click local server launcher (http://localhost:8080)
│
├── bd_geo.js                   # Bangladesh 8 Divisions GeoJSON boundaries
├── bd_districts_geo.js         # Bangladesh 64 Districts GeoJSON boundaries
├── bd_thanas_geo.js            # Bangladesh Upazilas / Thanas GeoJSON boundaries
├── bd_boundary.json            # Bangladesh National Boundary mask
│
├── ceo_national.js             # Nationwide KPI summaries & Division/District/Thana aggregates
├── ceo_outlets_D0.js           # Dhaka Division retail outlet dataset
├── ceo_outlets_D1.js           # Chattogram Division retail outlet dataset
├── ceo_outlets_D2.js           # Rajshahi Division retail outlet dataset
├── ceo_outlets_D3.js           # Khulna Division retail outlet dataset
├── ceo_outlets_D4.js           # Barishal Division retail outlet dataset
├── ceo_outlets_D5.js           # Sylhet Division retail outlet dataset
├── ceo_outlets_D6.js           # Rangpur Division retail outlet dataset
├── ceo_outlets_D7.js           # Mymensingh Division retail outlet dataset
│
├── pipeline/                   # Universal Data Processing Pipeline
│   ├── build_map_pipeline.py   # Universal Python script to process ANY company's CSV
│   └── sample_outlets_template.csv # Sample CSV showing exact column headers
│
└── geo_assets/                 # Raw GeoJSON archives (backup)
    ├── bd_divisions_raw.json
    ├── bd_raw.json
    └── bd_upazilas_raw.json
```

---

## 🚀 How to Implement with a New Company's Data (Step-by-Step)

You can generate the complete interactive map for **any company** in 3 simple steps:

### 🔹 Step 1: Prepare the Company Outlets Data
Create a CSV file (e.g. `company_outlets.csv`) following the schema in `pipeline/sample_outlets_template.csv`.

#### Required Columns:
| Column Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `outlet_id` | String | Unique ID or code of the retail store | `OUT-9821` |
| `outlet_name` | String | Name of the shop / retailer | `Bismillah Store` |
| `latitude` | Float | GPS Latitude (20.5 to 26.5) | `23.8103` |
| `longitude` | Float | GPS Longitude (88.0 to 92.5) | `90.4125` |
| `division` | String | Division name (Dhaka, Chattogram, etc.) | `Dhaka` |
| `district` | String | District name | `Gazipur` |
| `thana` | String | Upazila or Thana name | `Sreepur` |
| `revenue` | Float | Total delivered sales amount (BDT) | `45000.0` |
| `visits` | Integer | Total number of physical sales rep visits | `18` |
| `orders` | Integer | Total count of converted orders | `14` |
| `last_visit_date` | String | Date of last field visit (YYYY-MM-DD) | `2026-08-25` |
| `days_since_last_visit` | Integer | Number of days since last visit | `6` |
| `sr_name` | String | Name of the assigned Sales Representative | `Md. Rahim` |
| `trend_m1` ... `trend_m4` | Float | *(Optional)* Month-by-month revenue | `10000.0, 11500.0, ...` |

---

### 🔹 Step 2: Run the Automated Pipeline
Open your terminal / PowerShell in the template directory and run:

```bash
python pipeline/build_map_pipeline.py path/to/your/company_outlets.csv .
```

This single command will automatically:
1. Validate GPS coordinates and normalize division names.
2. Calculate composite 0-100 health scores, primary tiers, and 9-tier gap tags.
3. Generate the updated `ceo_national.js` and `ceo_outlets_D0.js` through `ceo_outlets_D7.js`.

---

### 🔹 Step 3: Launch and Present
Double click **`start_demo.bat`** or run:
```bash
python -m http.server 8080
```
Then open `http://localhost:8080/index.html` in your browser.

---

## 🌐 Deployment Options

1. **Vercel / Netlify / Cloudflare Pages:**
   - Push this entire folder to GitHub and deploy in 1 click (no build commands needed).
2. **Local / Intranet Server:**
   - Host via Python HTTP server, Apache, Nginx, or IIS.
3. **Portal / iFrame Integration:**
   - Embed `index.html` inside any ERP, React, Angular, or BI portal via `<iframe src="index.html"></iframe>`.

---

## 🔒 Data Privacy & Performance Guarantee
* All computations, cluster math, and geospatial filtering occur **100% on the client's browser (Client-Side Memory)**.
* No private company sales data is ever sent to external cloud APIs.
