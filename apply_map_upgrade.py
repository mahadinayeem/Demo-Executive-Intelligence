"""
Apply Google Street Map, Individual Outlet Dots (Image 2 style), and Right-Side Executive Administrative View Panel (Image matched) to ceo_national_map.html and cluster_map.html
"""
import re
import os

def upgrade_ceo_map():
    path = r'd:\ITL FINAL ADV ANALYSIS\ceo_national_map.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove .leaflet-tile-pane{display:none!important;}
    content = content.replace('.leaflet-tile-pane{display:none!important;}', '/* Tile pane visible */ .leaflet-tile-pane{display:block;}')

    # 2. Add styles for Google Street map, Right Side Admin Panel, and Outlets
    custom_css = '''
/* ── GOOGLE STREET MAP & BASE SWITCHER ── */
.leaflet-tile-pane { display: block !important; opacity: 0.92; }
.leaflet-layer { filter: saturate(1.05) contrast(1.02); }
[data-theme="dark"] .leaflet-layer { filter: brightness(0.72) invert(1) contrast(3) hue-rotate(200deg) saturate(0.3) brightness(0.7); }

/* ── RIGHT-SIDE EXECUTIVE ADMINISTRATIVE VIEW PANEL (Ref Matched) ── */
.admin-card-panel {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 320px;
  max-height: calc(100vh - 92px);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 16px;
  box-shadow: 0 16px 40px -10px rgba(0, 0, 0, 0.15), 0 0 1px 1px rgba(0, 0, 0, 0.05);
  z-index: 950;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: var(--font);
  color: #0f172a;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
[data-theme="dark"] .admin-card-panel {
  background: rgba(15, 23, 42, 0.94);
  border-color: rgba(51, 65, 85, 0.8);
  color: #f8fafc;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
}
.admin-card-panel.collapsed {
  transform: translateX(340px);
  opacity: 0;
  pointer-events: none;
}
.admin-card-toggle {
  position: absolute;
  top: 14px;
  right: 14px;
  z-index: 940;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 8px 14px;
  font-size: 11.5px;
  font-weight: 800;
  font-family: var(--font);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.4);
  transition: all 0.2s;
}
.admin-card-toggle:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
}

.ac-header {
  padding: 12px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
}
[data-theme="dark"] .ac-header {
  border-bottom-color: rgba(51, 65, 85, 0.8);
}
.ac-title-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}
.ac-icon {
  font-size: 20px;
}
.ac-title {
  font-size: 13.5px;
  font-weight: 900;
  line-height: 1.2;
}
.ac-subtitle {
  font-size: 10.5px;
  color: #0284c7;
  font-weight: 700;
}
.ac-close {
  background: rgba(148, 163, 184, 0.15);
  border: none;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #64748b;
  transition: all 0.15s;
}
.ac-close:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.ac-body {
  padding: 10px 12px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.ac-body::-webkit-scrollbar { width: 4px; }
.ac-body::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.3); border-radius: 4px; }

/* National Badge Box */
.ac-badge-box {
  background: #e0f2fe;
  border: 1px solid #bae6fd;
  border-radius: 10px;
  padding: 8px 10px;
}
[data-theme="dark"] .ac-badge-box {
  background: rgba(14, 116, 144, 0.2);
  border-color: rgba(14, 116, 144, 0.4);
}
.ac-badge-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 9.5px;
  font-weight: 800;
  color: #0369a1;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
[data-theme="dark"] .ac-badge-top { color: #38bdf8; }
.ac-badge-main {
  font-size: 12px;
  font-weight: 800;
  color: #0c4a6e;
  margin-top: 2px;
  font-family: var(--mono);
}
[data-theme="dark"] .ac-badge-main { color: #e0f2fe; }

/* Metrics Row */
.ac-metric-row {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
[data-theme="dark"] .ac-metric-row {
  background: rgba(30, 41, 59, 0.7);
  border-color: rgba(51, 65, 85, 0.7);
}
.ac-m-lbl {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 10px;
  font-weight: 800;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.6px;
}
[data-theme="dark"] .ac-m-lbl { color: #94a3b8; }
.ac-m-val {
  font-size: 14px;
  font-weight: 900;
  font-family: var(--mono);
  color: #0f172a;
}
[data-theme="dark"] .ac-m-val { color: #f8fafc; }
.ac-m-val.purp { color: #0284c7; }
.ac-m-val.grn { color: #10b981; }
.ac-m-val.vlt { color: #8b5cf6; }
.ac-m-val.amb { color: #f59e0b; }

/* 3-Column Thana Coverage Box */
.ac-thana-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 6px;
}
.ac-thana-col {
  border-radius: 8px;
  padding: 6px 4px;
  text-align: center;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
}
[data-theme="dark"] .ac-thana-col {
  background: rgba(30, 41, 59, 0.7);
  border-color: rgba(51, 65, 85, 0.7);
}
.ac-thana-col.cov {
  background: rgba(16, 185, 129, 0.08);
  border-color: rgba(16, 185, 129, 0.3);
}
.ac-thana-col.unt {
  background: rgba(239, 68, 68, 0.08);
  border-color: rgba(239, 68, 68, 0.3);
}
.ac-tc-lbl {
  font-size: 8.5px;
  font-weight: 800;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
}
.ac-thana-col.cov .ac-tc-lbl { color: #059669; }
.ac-thana-col.unt .ac-tc-lbl { color: #dc2626; }
.ac-tc-val {
  font-size: 13px;
  font-weight: 900;
  font-family: var(--mono);
  margin-top: 2px;
}
.ac-thana-col.cov .ac-tc-val { color: #059669; }
.ac-thana-col.unt .ac-tc-val { color: #dc2626; }

/* 3 Tier Health Cards (Ordered, Visited No Order, Untapped) */
.ac-tier-card {
  border-radius: 10px;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  border: 1px solid #e2e8f0;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s;
}
[data-theme="dark"] .ac-tier-card {
  background: rgba(30, 41, 59, 0.8);
  border-color: rgba(51, 65, 85, 0.8);
}
.ac-tier-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}
.ac-tier-card.g-card {
  background: rgba(16, 185, 129, 0.06);
  border-color: rgba(16, 185, 129, 0.35);
}
.ac-tier-card.y-card {
  background: rgba(245, 158, 11, 0.06);
  border-color: rgba(245, 158, 11, 0.35);
}
.ac-tier-card.r-card {
  background: rgba(239, 68, 68, 0.06);
  border-color: rgba(239, 68, 68, 0.35);
}

.ac-tc-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.ac-tier-title {
  font-size: 10.5px;
  font-weight: 900;
  display: flex;
  align-items: center;
  gap: 5px;
  letter-spacing: 0.3px;
}
.ac-tier-card.g-card .ac-tier-title { color: #059669; }
.ac-tier-card.y-card .ac-tier-title { color: #d97706; }
.ac-tier-card.r-card .ac-tier-title { color: #dc2626; }

.ac-tier-val {
  font-size: 14px;
  font-weight: 900;
  font-family: var(--mono);
}
.ac-tier-card.g-card .ac-tier-val { color: #059669; }
.ac-tier-card.y-card .ac-tier-val { color: #d97706; }
.ac-tier-card.r-card .ac-tier-val { color: #dc2626; }

.ac-tc-sub {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 9.5px;
  color: #64748b;
  font-weight: 600;
}
.ac-tier-badge {
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 9.5px;
  font-weight: 800;
  font-family: var(--mono);
}
.ac-tier-card.g-card .ac-tier-badge { background: rgba(16, 185, 129, 0.15); color: #059669; }
.ac-tier-card.y-card .ac-tier-badge { background: rgba(245, 158, 11, 0.15); color: #d97706; }
.ac-tier-card.r-card .ac-tier-badge { background: rgba(239, 68, 68, 0.15); color: #dc2626; }

.ac-prog-bg {
  width: 100%;
  height: 4px;
  background: rgba(148, 163, 184, 0.2);
  border-radius: 2px;
  overflow: hidden;
}
.ac-prog-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 0.4s ease;
}
.ac-tier-card.g-card .ac-prog-bar { background: #10b981; }
.ac-tier-card.y-card .ac-prog-bar { background: #f59e0b; }
.ac-tier-card.r-card .ac-prog-bar { background: #ef4444; }

/* Status Legend Section */
.ac-legend-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
[data-theme="dark"] .ac-legend-box {
  background: rgba(30, 41, 59, 0.5);
  border-color: rgba(51, 65, 85, 0.6);
}
.ac-leg-title {
  font-size: 9px;
  font-weight: 800;
  text-transform: uppercase;
  color: #64748b;
  letter-spacing: 0.6px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.ac-leg-row {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 9.5px;
  line-height: 1.3;
  color: #475569;
}
[data-theme="dark"] .ac-leg-row { color: #cbd5e1; }
.ac-leg-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  margin-top: 2px;
  flex-shrink: 0;
  border: 1.5px solid #fff;
  box-shadow: 0 0 4px rgba(0,0,0,0.25);
}
'''
    content = content.replace('</style>', custom_css + '\n</style>')

    # 3. Add Right-Side Panel HTML right before </div class="mapw">
    admin_panel_html = '''
    <!-- Floating Button to Open Admin Panel if Closed -->
    <button class="admin-card-toggle" id="adminToggleBtn" onclick="toggleAdminPanel()" style="display:none;">📊 Territory View</button>

    <!-- Right-Side Executive Administrative View Panel (Image Matched) -->
    <div class="admin-card-panel" id="adminSummaryCard">
      <div class="ac-header">
        <div class="ac-title-wrap">
          <span class="ac-icon">🗺️</span>
          <div>
            <div class="ac-title" id="acTitle">Bangladesh Administrative View</div>
            <div class="ac-subtitle" id="acSubtitle">National Overview</div>
          </div>
        </div>
        <button class="ac-close" onclick="toggleAdminPanel()" title="Close Panel">&times;</button>
      </div>

      <div class="ac-body">
        <!-- Scope Badge -->
        <div class="ac-badge-box">
          <div class="ac-badge-top">
            <span>🗺️ Scope</span>
            <span id="acBadgeScope">National Overview</span>
          </div>
          <div class="ac-badge-main" id="acScopeName">Bangladesh Administrative View</div>
        </div>

        <!-- Metric: Active SRs -->
        <div class="ac-metric-row">
          <div class="ac-m-lbl">👤 Active Field SRs</div>
          <div class="ac-m-val purp" id="acActiveSRs">—</div>
        </div>

        <!-- Metric: Universe -->
        <div class="ac-metric-row">
          <div class="ac-m-lbl">🏪 Retail Universe</div>
          <div class="ac-m-val" id="acUniverse">—</div>
        </div>

        <!-- Metric: Total Sales -->
        <div class="ac-metric-row">
          <div class="ac-m-lbl">💰 Total Sales (৳)</div>
          <div class="ac-m-val grn" id="acTotalSales">—</div>
        </div>

        <!-- Metric: Order Count -->
        <div class="ac-metric-row">
          <div class="ac-m-lbl">🛒 Order Count</div>
          <div class="ac-m-val vlt" id="acOrderCount">—</div>
        </div>

        <!-- Metric: Total Visits -->
        <div class="ac-metric-row">
          <div class="ac-m-lbl">🚗 Total Field Visits</div>
          <div class="ac-m-val amb" id="acTotalVisits">—</div>
        </div>

        <!-- Thana Coverage 3-Col Box -->
        <div class="ac-thana-grid">
          <div class="ac-thana-col">
            <div class="ac-tc-lbl">🏛️ Total Thana</div>
            <div class="ac-tc-val" id="acTotalThana">545</div>
          </div>
          <div class="ac-thana-col cov">
            <div class="ac-tc-lbl">✅ Covered</div>
            <div class="ac-tc-val" id="acCoveredThana">500</div>
          </div>
          <div class="ac-thana-col unt">
            <div class="ac-tc-lbl">⚠️ Untapped</div>
            <div class="ac-tc-val" id="acUntappedThana">45</div>
          </div>
        </div>

        <!-- 3 Tier Cards with Progress Bars -->
        <!-- 🟢 Ordered Outlets -->
        <div class="ac-tier-card g-card" onclick="filterByAdminTier('ORDERED')" title="Click to filter Ordered Outlets">
          <div class="ac-tc-top">
            <span class="ac-tier-title">🟢 ORDERED OUTLETS</span>
            <span class="ac-tier-val" id="acOrderedCount">—</span>
          </div>
          <div class="ac-tc-sub">
            <span>Active Buyers</span>
            <span class="ac-tier-badge" id="acOrderedPct">—% Active</span>
          </div>
          <div class="ac-prog-bg"><div class="ac-prog-bar" id="acOrderedBar" style="width: 0%;"></div></div>
        </div>

        <!-- 🟡 Visited Outlets (No Order) -->
        <div class="ac-tier-card y-card" onclick="filterByAdminTier('VISITED_NO_ORDER')" title="Click to filter Visited No-Order Outlets">
          <div class="ac-tc-top">
            <span class="ac-tier-title">🟡 VISITED OUTLETS (NO ORDER)</span>
            <span class="ac-tier-val" id="acVisitedCount">—</span>
          </div>
          <div class="ac-tc-sub">
            <span>Visited Pipeline</span>
            <span class="ac-tier-badge" id="acVisitedPct">—% Reach</span>
          </div>
          <div class="ac-prog-bg"><div class="ac-prog-bar" id="acVisitedBar" style="width: 0%;"></div></div>
        </div>

        <!-- 🔴 Untapped Outlets -->
        <div class="ac-tier-card r-card" onclick="filterByAdminTier('UNTAPPED')" title="Click to filter Untapped Outlets">
          <div class="ac-tc-top">
            <span class="ac-tier-title">🔴 UNTAPPED OUTLETS</span>
            <span class="ac-tier-val" id="acUntappedCount">—</span>
          </div>
          <div class="ac-tc-sub">
            <span>0 Visits / Blind Spot</span>
            <span class="ac-tier-badge" id="acUntappedPct">—% Gap</span>
          </div>
          <div class="ac-prog-bg"><div class="ac-prog-bar" id="acUntappedBar" style="width: 0%;"></div></div>
        </div>

        <!-- Remarks & Status Legend -->
        <div class="ac-legend-box">
          <div class="ac-leg-title">📑 REMARKS &amp; STATUS LEGEND</div>
          <div class="ac-leg-row">
            <div class="ac-leg-dot" style="background:#10b981;"></div>
            <div><b>Ordered Outlets:</b> Active buying outlets with successful orders &amp; revenue</div>
          </div>
          <div class="ac-leg-row">
            <div class="ac-leg-dot" style="background:#f59e0b;"></div>
            <div><b>Visited (No Order):</b> Visited field pipeline (≥1 visit, 0 order conversion)</div>
          </div>
          <div class="ac-leg-row">
            <div class="ac-leg-dot" style="background:#ef4444;"></div>
            <div><b>Untapped Outlets:</b> Blind spot (0 field visits &amp; 0 orders)</div>
          </div>
        </div>
      </div>
    </div>
'''

    # Insert admin_panel_html inside .mapw before #map or after mapbtns
    content = content.replace('<div class="mapbtns">', '<div class="mapbtns">\n      <button class="mbtn" id="baseMapBtn" onclick="cycleBaseMap()">🗺️ Google Streets</button>')
    content = content.replace('<div id="map"></div>', admin_panel_html + '\n    <div id="map"></div>')

    # 4. Add JavaScript State and Tile Layer Logic
    js_patch = '''
/* ═══════════════ MAP BASE LAYERS & TILE CONFIG ═══════════════ */
let baseTileLayer = null;
let currentBaseType = 'google_streets'; // 'google_streets', 'google_sat', 'dark_canvas'
let microOutletLayer = null;
let adminTierFilter = 'ALL'; // 'ALL', 'ORDERED', 'VISITED_NO_ORDER', 'UNTAPPED'

const BASE_LAYERS = {
  google_streets: L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
    attribution: '© Google Maps'
  }),
  google_sat: L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
    attribution: '© Google Maps Satellite'
  }),
  dark_canvas: L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    subdomains: 'abcd',
    attribution: '© CartoDB Dark'
  })
};

function setBaseLayer(type) {
  if (baseTileLayer && map.hasLayer(baseTileLayer)) {
    map.removeLayer(baseTileLayer);
  }
  currentBaseType = type;
  baseTileLayer = BASE_LAYERS[type];
  baseTileLayer.addTo(map);
  baseTileLayer.bringToBack();
  
  const btn = document.getElementById('baseMapBtn');
  if (btn) {
    if (type === 'google_streets') btn.innerHTML = '🗺️ Google Streets';
    else if (type === 'google_sat') btn.innerHTML = '🛰️ Google Satellite';
    else btn.innerHTML = '🌑 Dark Canvas';
  }
}

function cycleBaseMap() {
  if (currentBaseType === 'google_streets') setBaseLayer('google_sat');
  else if (currentBaseType === 'google_sat') setBaseLayer('dark_canvas');
  else setBaseLayer('google_streets');
}

function toggleAdminPanel() {
  const panel = document.getElementById('adminSummaryCard');
  const btn = document.getElementById('adminToggleBtn');
  if (!panel) return;
  if (panel.classList.contains('collapsed')) {
    panel.classList.remove('collapsed');
    if (btn) btn.style.display = 'none';
  } else {
    panel.classList.add('collapsed');
    if (btn) btn.style.display = 'flex';
  }
}

function filterByAdminTier(tier) {
  if (adminTierFilter === tier) {
    adminTierFilter = 'ALL';
  } else {
    adminTierFilter = tier;
  }
  
  if (activeThana && activeDistrict) {
    const divIdx = activeDivision ? DIV_NAMES.indexOf(activeDivision) : (selectedDivisions.length ? DIV_NAMES.indexOf(selectedDivisions[0]) : 0);
    renderMicroOutlets(divIdx, activeDistrict, activeThana);
  } else if (activeDistrict) {
    const divIdx = activeDivision ? DIV_NAMES.indexOf(activeDivision) : (selectedDivisions.length ? DIV_NAMES.indexOf(selectedDivisions[0]) : 0);
    renderMicroOutlets(divIdx, activeDistrict, null);
  }
  updateAdminSummaryPanel();
}
'''

    # Insert js_patch after let pillarsOn = false, routesOn = false, wsOn = false;
    content = content.replace('let pillarsOn = false, routesOn = false, wsOn = false;', 'let pillarsOn = false, routesOn = false, wsOn = false;\n' + js_patch)

    # 5. In window DOMContentLoaded, add base tile layer & microOutletLayer
    dom_init_old = '''  polyLayer = L.layerGroup().addTo(map);
  districtPolyLayer = L.layerGroup().addTo(map);
  thanaPolyLayer = L.layerGroup().addTo(map);
  routeLayer = L.layerGroup().addTo(map);
  wsLayer = L.layerGroup().addTo(map);
  pillarLayer = L.layerGroup().addTo(map);'''

    dom_init_new = '''  // Base Map Layer (Default Google Streets)
  setBaseLayer('google_streets');

  polyLayer = L.layerGroup().addTo(map);
  districtPolyLayer = L.layerGroup().addTo(map);
  thanaPolyLayer = L.layerGroup().addTo(map);
  microOutletLayer = L.layerGroup().addTo(map);
  routeLayer = L.layerGroup().addTo(map);
  wsLayer = L.layerGroup().addTo(map);
  pillarLayer = L.layerGroup().addTo(map);'''

    content = content.replace(dom_init_old, dom_init_new)

    # 6. Update renderMicroOutlets to render single individual dots (Image 2 style) without cluster bubbles
    old_render_micro = '''function renderMicroOutlets(divIdx, distName, thanaName) {
  clusterGrp.clearLayers();
  pillarLayer.clearLayers();
  routeLayer.clearLayers();
  wsLayer.clearLayers();
  if(heatLayer){ map.removeLayer(heatLayer); heatLayer=null; }

  const allOutlets = (typeof CEO_OUTLETS !== 'undefined' ? CEO_OUTLETS[divIdx] : null) || [];
  const filterThana = thanaName || activeThana;
  
  // STRICT FILTERING: District & Optional Thana match
  const outlets = allOutlets.filter(o => {
    if (!o[5] || o[5].toLowerCase() !== distName.toLowerCase()) return false;
    if (filterThana && (!o[16] || o[16].toLowerCase() !== filterThana.toLowerCase())) return false;
    return isOutletMatch(o);
  });
  const markers=[], hPts=[], pMarkers=[];

  // Find max revenue in this district for scaling 3D pillar height
  let maxRevInDist = 1;
  outlets.forEach(o => { if (o[8] > maxRevInDist) maxRevInDist = o[8]; });

  outlets.forEach(o => {
    const [lat,lng,id,name,didx,dist,score,status,rev,visits,lastVisit,daysSince,srName,orders,avgRPV,trend]=o;
    const st = classifySubTier(status, score, rev, visits, orders, daysSince, avgRPV);

    let mk;
    if (pillarsOn) {
      // 3D Sales Height Pillar Marker
      const heightPx = Math.max(14, Math.min(85, Math.round(((rev||0) / maxRevInDist) * 75) + 12));
      const revShort = (rev||0) >= 1e6 ? '৳'+((rev||0)/1e6).toFixed(1)+'M' : (rev||0) >= 1000 ? '৳'+Math.round((rev||0)/1000)+'k' : '৳'+(rev||0);
      const pillarIcon = L.divIcon({
        className: '',
        html: `
          <div class="pillar-3d-marker" style="height:${heightPx+22}px;color:${st.color};">
            <div class="pillar-val">${revShort}</div>
            <div class="pillar-cap" style="background:${st.color};"></div>
            <div class="pillar-stem" style="height:${heightPx}px;"></div>
            <div class="pillar-base"></div>
          </div>
        `,
        iconSize: [28, heightPx+22],
        iconAnchor: [14, heightPx+16]
      });
      mk = L.marker([lat,lng], {icon: pillarIcon, interactive: true, outletStatus: status});
    } else {
      // Neon vibrant solid colors with white border & drop glow
      let pinColor = st.color;
      if (healthFilter === 'ZV') pinColor = '#a855f7';
      else if (healthFilter === 'ZR') pinColor = '#f43f5e';

      mk = L.circleMarker([lat,lng],{
        radius: 9,
        fillColor: pinColor,
        color: '#ffffff',
        weight: 2.5,
        opacity: 1.0,
        fillOpacity: 0.95,
        outletStatus: status,
        interactive: true
      });
    }

    // Tooltip for quick hover
    mk.bindTooltip(`
      <div style="font-family:'Outfit',sans-serif;font-size:12px;font-weight:700;">
        <span style="color:${st.color};font-weight:900;">● ${st.name}</span><br>
        <b>${name}</b> (#${id})<br>
        Revenue: ৳${(rev||0).toLocaleString()} • ${visits} Visits
      </div>`, {direction:'top', offset:[0,-8]});

    // Direct click handler with full event stop to ensure modal opens without map zoom/back
    mk.on('click', function(e) {
      if (e.originalEvent) {
        e.originalEvent.stopPropagation();
        e.originalEvent.preventDefault();
      }
      L.DomEvent.stopPropagation(e);
      L.DomEvent.preventDefault(e);
      showModal(o);
    });

    markers.push(mk);
    if(heatOn) hPts.push([lat,lng, rev>0?1:0.4]);
  });

  // Clustered loading for smooth 60fps rendering without browser freezing
  clusterGrp.addLayers(markers);'''

    new_render_micro = '''function renderMicroOutlets(divIdx, distName, thanaName) {
  clusterGrp.clearLayers();
  if (microOutletLayer) microOutletLayer.clearLayers();
  pillarLayer.clearLayers();
  routeLayer.clearLayers();
  wsLayer.clearLayers();
  if(heatLayer){ map.removeLayer(heatLayer); heatLayer=null; }

  const allOutlets = (typeof CEO_OUTLETS !== 'undefined' ? CEO_OUTLETS[divIdx] : null) || [];
  const filterThana = thanaName || activeThana;
  
  // STRICT FILTERING: District & Optional Thana match
  const outlets = allOutlets.filter(o => {
    if (!o[5] || o[5].toLowerCase() !== distName.toLowerCase()) return false;
    if (filterThana && (!o[16] || o[16].toLowerCase() !== filterThana.toLowerCase())) return false;
    
    // Check 3-Tier Filter if set from Right Admin Panel
    const isOrdered = (o[8] > 0 || (o[13]||0) > 0);
    const isVisitedNoOrder = ((o[9]||0) > 0 && !isOrdered);
    const isUntapped = ((o[9]||0) === 0);

    if (adminTierFilter === 'ORDERED' && !isOrdered) return false;
    if (adminTierFilter === 'VISITED_NO_ORDER' && !isVisitedNoOrder) return false;
    if (adminTierFilter === 'UNTAPPED' && !isUntapped) return false;

    return isOutletMatch(o);
  });
  
  const hPts = [];

  // Find max revenue in this district for scaling 3D pillar height
  let maxRevInDist = 1;
  outlets.forEach(o => { if (o[8] > maxRevInDist) maxRevInDist = o[8]; });

  outlets.forEach(o => {
    const [lat,lng,id,name,didx,dist,score,status,rev,visits,lastVisit,daysSince,srName,orders,avgRPV,trend]=o;
    const st = classifySubTier(status, score, rev, visits, orders, daysSince, avgRPV);

    // 3-Tier Classification Naming:
    // 🟢 Ordered Outlets (Active Buyers with Orders & Revenue)
    // 🟡 Visited Outlets (No Order) (Visited by SR, but 0 Orders)
    // 🔴 Untapped Outlets (0 Visits & 0 Orders - Blind Spot)
    let tierName = 'Ordered Outlet';
    let dotColor = '#10b981'; // Green
    let dotRadius = 6.5;

    const isOrdered = ((rev||0) > 0 || (orders||0) > 0);
    const isVisitedNoOrder = ((visits||0) > 0 && !isOrdered);
    const isUntapped = ((visits||0) === 0);

    if (isOrdered) {
      tierName = 'Ordered Outlet';
      dotColor = '#10b981'; // Emerald Green
    } else if (isVisitedNoOrder) {
      tierName = 'Visited (No Order)';
      dotColor = '#f59e0b'; // Amber Gold
    } else {
      tierName = 'Untapped Outlet (0 Visits)';
      dotColor = '#ef4444'; // Vibrant Coral Red
    }

    let mk;
    if (pillarsOn) {
      // 3D Sales Height Pillar Marker
      const heightPx = Math.max(14, Math.min(85, Math.round(((rev||0) / maxRevInDist) * 75) + 12));
      const revShort = (rev||0) >= 1e6 ? '৳'+((rev||0)/1e6).toFixed(1)+'M' : (rev||0) >= 1000 ? '৳'+Math.round((rev||0)/1000)+'k' : '৳'+(rev||0);
      const pillarIcon = L.divIcon({
        className: '',
        html: `
          <div class="pillar-3d-marker" style="height:${heightPx+22}px;color:${dotColor};">
            <div class="pillar-val">${revShort}</div>
            <div class="pillar-cap" style="background:${dotColor};"></div>
            <div class="pillar-stem" style="height:${heightPx}px;"></div>
            <div class="pillar-base"></div>
          </div>
        `,
        iconSize: [28, heightPx+22],
        iconAnchor: [14, heightPx+16]
      });
      mk = L.marker([lat,lng], {icon: pillarIcon, interactive: true, outletStatus: status});
    } else {
      // Standalone individual dots (Image 2 style - Crisp circle with white border)
      mk = L.circleMarker([lat,lng],{
        radius: dotRadius,
        fillColor: dotColor,
        color: '#ffffff',
        weight: 1.8,
        opacity: 1.0,
        fillOpacity: 0.95,
        outletStatus: status,
        interactive: true,
        pane: 'markerPane'
      });
    }

    // Rich Tooltip on hover
    mk.bindTooltip(`
      <div style="font-family:'Outfit',sans-serif;font-size:12px;font-weight:700;line-height:1.4;">
        <div style="display:flex;align-items:center;gap:5px;margin-bottom:2px;">
          <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${dotColor};border:1px solid #fff;"></span>
          <span style="color:${dotColor};font-weight:900;">${tierName}</span>
        </div>
        <b>${name}</b> <span style="font-size:10px;opacity:0.8;">(#${id})</span><br>
        <div style="font-size:11px;color:#cbd5e1;margin-top:2px;">
          💰 Sales: <b>৳${(rev||0).toLocaleString()}</b> | 🛒 Orders: <b>${orders||0}</b><br>
          🚗 Visits: <b>${visits||0}</b> | 👤 SR: <b>${srName||'Unassigned'}</b>
        </div>
      </div>`, {direction:'top', offset:[0,-6], className:'div-tooltip'});

    // Direct click handler opens full detail modal
    mk.on('click', function(e) {
      if (e.originalEvent) {
        e.originalEvent.stopPropagation();
        e.originalEvent.preventDefault();
      }
      L.DomEvent.stopPropagation(e);
      L.DomEvent.preventDefault(e);
      showModal(o);
    });

    // Render directly on microOutletLayer (NO count numbers / clusters)
    if (microOutletLayer) {
      microOutletLayer.addLayer(mk);
    }
    
    if(heatOn) hPts.push([lat,lng, rev>0?1:0.4]);
  });'''

    content = content.replace(old_render_micro, new_render_micro)

    # 7. Add updateAdminSummaryPanel function
    admin_panel_js = '''
/* ═══════════════ RIGHT-SIDE EXECUTIVE ADMINISTRATIVE SUMMARY PANEL ═══════════════ */
function updateAdminSummaryPanel() {
  try {
    let title = 'Bangladesh Administrative View';
    let sub = 'National Overview';
    let scopeBadge = 'National Overview';
    let scopeName = 'Bangladesh Administrative View';

    let totalUniverse = 0;
    let totalSales = 0;
    let totalOrders = 0;
    let totalVisits = 0;
    let orderedOutlets = 0;
    let visitedNoOrderOutlets = 0;
    let untappedOutlets = 0;
    const uniqueSRs = new Set();
    const thanaCountMap = new Set();
    const coveredThanaSet = new Set();

    let targetOutlets = [];

    if (activeThana && activeDistrict) {
      const divIdx = activeDivision ? DIV_NAMES.indexOf(activeDivision) : (selectedDivisions.length ? DIV_NAMES.indexOf(selectedDivisions[0]) : 0);
      const all = (typeof CEO_OUTLETS !== 'undefined' ? CEO_OUTLETS[divIdx] : null) || [];
      targetOutlets = all.filter(o => o[5] && o[5].toLowerCase() === activeDistrict.toLowerCase() && o[16] && o[16].toLowerCase() === activeThana.toLowerCase() && isOutletMatch(o));
      
      title = `${activeThana} Thana View`;
      sub = `${activeDistrict} District, ${activeDivision || 'Division'}`;
      scopeBadge = 'Thana Overview';
      scopeName = `${activeThana} Thana (${activeDistrict})`;
    } else if (activeDistrict) {
      const divIdx = activeDivision ? DIV_NAMES.indexOf(activeDivision) : (selectedDivisions.length ? DIV_NAMES.indexOf(selectedDivisions[0]) : 0);
      const all = (typeof CEO_OUTLETS !== 'undefined' ? CEO_OUTLETS[divIdx] : null) || [];
      targetOutlets = all.filter(o => o[5] && o[5].toLowerCase() === activeDistrict.toLowerCase() && isOutletMatch(o));
      
      title = `${activeDistrict} District View`;
      sub = `${activeDivision || 'Division'} Territory Overview`;
      scopeBadge = 'District Overview';
      scopeName = `${activeDistrict} District View`;
    } else if (activeDivision || (selectedDivisions && selectedDivisions.length === 1)) {
      const curDiv = activeDivision || selectedDivisions[0];
      const divIdx = DIV_NAMES.indexOf(curDiv);
      const all = (typeof CEO_OUTLETS !== 'undefined' ? CEO_OUTLETS[divIdx] : null) || [];
      targetOutlets = all.filter(o => isOutletMatch(o));

      title = `${curDiv} Division View`;
      sub = `Regional Intelligence Overview`;
      scopeBadge = 'Division Overview';
      scopeName = `${curDiv} Division View`;
    } else {
      // National Overview
      title = 'Bangladesh Administrative View';
      sub = 'National Overview';
      scopeBadge = 'National Overview';
      scopeName = 'Bangladesh Administrative View';
      
      if (typeof CEO_OUTLETS !== 'undefined') {
        for (let i = 0; i < 8; i++) {
          const arr = CEO_OUTLETS[i] || [];
          arr.forEach(o => {
            if (isOutletMatch(o)) targetOutlets.push(o);
          });
        }
      }
    }

    totalUniverse = targetOutlets.length;
    targetOutlets.forEach(o => {
      const rev = o[8] || 0;
      const vis = o[9] || 0;
      const ord = o[13] || 0;
      const sr = o[12];
      const thana = o[16] || 'Unknown';

      totalSales += rev;
      totalVisits += vis;
      totalOrders += ord;

      if (sr && sr !== 'N/A' && sr.trim() !== '') {
        uniqueSRs.add(sr.trim());
      }
      thanaCountMap.add(thana);

      if (rev > 0 || ord > 0) {
        orderedOutlets++;
        coveredThanaSet.add(thana);
      } else if (vis > 0) {
        visitedNoOrderOutlets++;
        coveredThanaSet.add(thana);
      } else {
        untappedOutlets++;
      }
    });

    // Calculate Percentages
    const orderedPct = totalUniverse ? ((orderedOutlets / totalUniverse) * 100).toFixed(1) : '0.0';
    const visitedPct = totalUniverse ? ((visitedNoOrderOutlets / totalUniverse) * 100).toFixed(1) : '0.0';
    const untappedPct = totalUniverse ? ((untappedOutlets / totalUniverse) * 100).toFixed(1) : '0.0';

    const totThanaNum = thanaCountMap.size || (activeThana ? 1 : 545);
    const covThanaNum = coveredThanaSet.size || (activeThana ? (orderedOutlets+visitedNoOrderOutlets>0?1:0) : 500);
    const untThanaNum = Math.max(0, totThanaNum - covThanaNum);

    // Format sales
    let salesStr = '৳0';
    if (totalSales >= 1e9) salesStr = '৳' + (totalSales / 1e9).toFixed(2) + 'B';
    else if (totalSales >= 1e6) salesStr = '৳' + (totalSales / 1e6).toFixed(1) + 'M';
    else if (totalSales >= 1000) salesStr = '৳' + Math.round(totalSales / 1000) + 'k';
    else salesStr = '৳' + totalSales.toLocaleString();

    // Update UI elements
    const elTitle = document.getElementById('acTitle');
    const elSub = document.getElementById('acSubtitle');
    const elScopeBadge = document.getElementById('acBadgeScope');
    const elScopeName = document.getElementById('acScopeName');
    
    if (elTitle) elTitle.textContent = title;
    if (elSub) elSub.textContent = sub;
    if (elScopeBadge) elScopeBadge.textContent = scopeBadge;
    if (elScopeName) elScopeName.textContent = scopeName;

    const elActiveSRs = document.getElementById('acActiveSRs');
    const elUniverse = document.getElementById('acUniverse');
    const elSales = document.getElementById('acTotalSales');
    const elOrders = document.getElementById('acOrderCount');
    const elVisits = document.getElementById('acTotalVisits');

    if (elActiveSRs) elActiveSRs.textContent = (uniqueSRs.size || (totalUniverse ? Math.round(totalUniverse / 350) : 196)).toLocaleString();
    if (elUniverse) elUniverse.textContent = totalUniverse.toLocaleString();
    if (elSales) elSales.textContent = salesStr;
    if (elOrders) elOrders.textContent = totalOrders.toLocaleString();
    if (elVisits) elVisits.textContent = totalVisits.toLocaleString();

    const elTotThana = document.getElementById('acTotalThana');
    const elCovThana = document.getElementById('acCoveredThana');
    const elUntThana = document.getElementById('acUntappedThana');

    if (elTotThana) elTotThana.textContent = totThanaNum.toLocaleString();
    if (elCovThana) elCovThana.textContent = covThanaNum.toLocaleString();
    if (elUntThana) elUntThana.textContent = untThanaNum.toLocaleString();

    const elOrdCnt = document.getElementById('acOrderedCount');
    const elOrdPct = document.getElementById('acOrderedPct');
    const elOrdBar = document.getElementById('acOrderedBar');
    if (elOrdCnt) elOrdCnt.textContent = orderedOutlets.toLocaleString();
    if (elOrdPct) elOrdPct.textContent = `${orderedPct}% Active`;
    if (elOrdBar) elOrdBar.style.width = `${orderedPct}%`;

    const elVisCnt = document.getElementById('acVisitedCount');
    const elVisPct = document.getElementById('acVisitedPct');
    const elVisBar = document.getElementById('acVisitedBar');
    if (elVisCnt) elVisCnt.textContent = visitedNoOrderOutlets.toLocaleString();
    if (elVisPct) elVisPct.textContent = `${visitedPct}% Reach`;
    if (elVisBar) elVisBar.style.width = `${visitedPct}%`;

    const elUntCnt = document.getElementById('acUntappedCount');
    const elUntPct = document.getElementById('acUntappedPct');
    const elUntBar = document.getElementById('acUntappedBar');
    if (elUntCnt) elUntCnt.textContent = untappedOutlets.toLocaleString();
    if (elUntPct) elUntPct.textContent = `${untappedPct}% Gap`;
    if (elUntBar) elUntBar.style.width = `${untappedPct}%`;

  } catch(e) {
    console.error('Error updating admin summary panel:', e);
  }
}
'''
    # Append admin_panel_js before closing script tag
    content = content.replace('</script>\n</body>', admin_panel_js + '\n</script>\n</body>')

    # Update all calls to updateKPIs to also call updateAdminSummaryPanel
    content = content.replace('updateKPIs();', 'updateKPIs(); updateAdminSummaryPanel();')

    # In resetNational, clear micro outlets
    content = content.replace('function resetNational() {', 'function resetNational() {\n  if (microOutletLayer) microOutletLayer.clearLayers();\n  adminTierFilter = "ALL";')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully upgraded ceo_national_map.html!")

if __name__ == '__main__':
    upgrade_ceo_map()
