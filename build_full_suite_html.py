import json

with open(r"E:\ITL FINAL ADV ANALYSIS\module1_full_suite_data.json", "r", encoding="utf-8") as f:
    suite_json = f.read()

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Geo-Intelligence Explorer™ - Complete 7 Module Visualizer</title>
    <!-- Leaflet & Extensions -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
    <script src="https://unpkg.com/leaflet-heat@0.2.0/dist/leaflet-heat.js"></script>
    <style>
        :root {{
            --bg-dark: #080c14;
            --panel-bg: rgba(14, 21, 37, 0.94);
            --card-border: rgba(255, 255, 255, 0.1);
            --accent-cyan: #00f2fe;
            --accent-blue: #38bdf8;
            --accent-green: #10b981;
            --accent-orange: #f59e0b;
            --accent-red: #ef4444;
            --accent-purple: #a855f7;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}
        body {{
            background: var(--bg-dark);
            color: var(--text-primary);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        /* Top Navigation Bar */
        header {{
            height: 68px;
            background: #0f172a;
            border-bottom: 1px solid var(--card-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            z-index: 1000;
        }}
        .brand-section {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .brand-pill {{
            background: linear-gradient(135deg, #00f2fe 0%, #3b82f6 100%);
            color: #080c14;
            font-weight: 800;
            font-size: 12px;
            padding: 5px 10px;
            border-radius: 6px;
            letter-spacing: 0.8px;
        }}
        .brand-title {{
            font-size: 19px;
            font-weight: 800;
            letter-spacing: -0.3px;
        }}
        .header-stats {{
            display: flex;
            gap: 16px;
        }}
        .stat-card {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 6px 14px;
            display: flex;
            flex-direction: column;
        }}
        .stat-card .label {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
        }}
        .stat-card .value {{
            font-size: 14px;
            font-weight: 700;
            color: var(--accent-cyan);
        }}
        /* Main Workspace */
        .workspace {{
            display: flex;
            flex: 1;
            position: relative;
            overflow: hidden;
        }}
        /* Left Navigation for the 7 Maps */
        .sidebar {{
            width: 360px;
            background: var(--panel-bg);
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--card-border);
            display: flex;
            flex-direction: column;
            padding: 18px;
            gap: 14px;
            overflow-y: auto;
            z-index: 999;
        }}
        .sidebar-section-title {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-secondary);
            margin-top: 4px;
        }}
        .nav-map-btn {{
            width: 100%;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            padding: 12px 14px;
            text-align: left;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            gap: 12px;
            color: var(--text-primary);
        }}
        .nav-map-btn:hover {{
            background: rgba(255, 255, 255, 0.08);
            border-color: var(--accent-blue);
            transform: translateX(3px);
        }}
        .nav-map-btn.active {{
            background: linear-gradient(135deg, rgba(0, 242, 254, 0.15) 0%, rgba(59, 130, 246, 0.2) 100%);
            border-color: var(--accent-cyan);
            box-shadow: 0 4px 20px rgba(0, 242, 254, 0.15);
        }}
        .nav-map-btn .icon-box {{
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            background: rgba(255, 255, 255, 0.05);
        }}
        .nav-map-btn .btn-text {{
            display: flex;
            flex-direction: column;
            flex: 1;
        }}
        .nav-map-btn .btn-title {{
            font-size: 13px;
            font-weight: 700;
        }}
        .nav-map-btn .btn-desc {{
            font-size: 11px;
            color: var(--text-secondary);
            margin-top: 2px;
        }}
        /* Info & Diagnostic Overlay Box */
        .diagnostic-card {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            padding: 14px;
        }}
        .diagnostic-header {{
            font-size: 12px;
            font-weight: 700;
            color: var(--accent-cyan);
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .diagnostic-body {{
            font-size: 12px;
            line-height: 1.5;
            color: var(--text-secondary);
        }}
        /* Map Canvas */
        #map {{
            flex: 1;
            height: 100%;
            background: #090d16;
        }}
        /* Popups */
        .leaflet-popup-content-wrapper {{
            background: #0f172a !important;
            color: #f8fafc !important;
            border: 1px solid var(--card-border) !important;
            border-radius: 12px !important;
            box-shadow: 0 20px 40px rgba(0,0,0,0.6) !important;
        }}
        .leaflet-popup-tip {{
            background: #0f172a !important;
        }}
        .pop-title {{
            font-size: 14px;
            font-weight: 800;
            color: var(--accent-cyan);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 6px;
            margin-bottom: 8px;
        }}
        .pop-row {{
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            margin-bottom: 4px;
            gap: 16px;
        }}
        .pop-label {{
            color: var(--text-secondary);
        }}
        .pop-val {{
            font-weight: 700;
        }}
        /* 3D Pillar Style Marker */
        .pillar-icon {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-end;
        }}
        .pillar-bar {{
            width: 8px;
            background: linear-gradient(to top, #00f2fe, #38bdf8, #ffffff);
            border-radius: 3px 3px 0 0;
            box-shadow: 0 0 10px rgba(0,242,254,0.8);
        }}
    </style>
</head>
<body>
    <header>
        <div class="brand-section">
            <span class="brand-pill">SOKRIO</span>
            <div class="brand-title">Geo-Intelligence Explorer™ <span style="font-size: 13px; font-weight: 500; color: var(--text-secondary);">| 7 Dedicated Geospatial Frameworks</span></div>
        </div>
        <div class="header-stats">
            <div class="stat-card">
                <span class="label">Total Universe</span>
                <span class="value">282,171 Stores</span>
            </div>
            <div class="stat-card">
                <span class="label">Active Buyers</span>
                <span class="value" style="color: var(--accent-green);">208,831 (74.0%)</span>
            </div>
            <div class="stat-card">
                <span class="label">Blind Spots</span>
                <span class="value" style="color: var(--accent-red);">73,453 (26.0%)</span>
            </div>
            <div class="stat-card">
                <span class="label">Net Sales</span>
                <span class="value" style="color: var(--accent-orange);">BDT 475.92 Cr</span>
            </div>
        </div>
    </header>

    <div class="workspace">
        <div class="sidebar">
            <div class="sidebar-section-title">Select Dedicated Framework (1 to 7)</div>

            <button class="nav-map-btn active" id="btn-mode-1" onclick="switchMapMode(1)">
                <div class="icon-box" style="color: var(--accent-cyan);">🌐</div>
                <div class="btn-text">
                    <span class="btn-title">1. Nationwide Retail Footprint</span>
                    <span class="btn-desc">Registered vs Active Stores Nationwide</span>
                </div>
            </button>

            <button class="nav-map-btn" id="btn-mode-2" onclick="switchMapMode(2)">
                <div class="icon-box" style="color: #ff5722;">🔥</div>
                <div class="btn-text">
                    <span class="btn-title">2. Visit Density & Heatmap</span>
                    <span class="btn-desc">Operational Intensity & Coverage Density</span>
                </div>
            </button>

            <button class="nav-map-btn" id="btn-mode-3" onclick="switchMapMode(3)">
                <div class="icon-box" style="color: var(--accent-red);">⚠️</div>
                <div class="btn-text">
                    <span class="btn-title">3. Operational Blind Spots</span>
                    <span class="btn-desc">73,453 Unvisited Stores & Field Accountability</span>
                </div>
            </button>

            <button class="nav-map-btn" id="btn-mode-4" onclick="switchMapMode(4)">
                <div class="icon-box" style="color: var(--accent-purple);">🚀</div>
                <div class="btn-text">
                    <span class="btn-title">4. White Space & Expansion</span>
                    <span class="btn-desc">High Potential Underserved Market Clusters</span>
                </div>
            </button>

            <button class="nav-map-btn" id="btn-mode-5" onclick="switchMapMode(5)">
                <div class="icon-box" style="color: var(--accent-blue);">📊</div>
                <div class="btn-text">
                    <span class="btn-title">5. 3D Sales Height & Tiering</span>
                    <span class="btn-desc">Extruded Volume Pillars & High Value Outlets</span>
                </div>
            </button>

            <button class="nav-map-btn" id="btn-mode-6" onclick="switchMapMode(6)">
                <div class="icon-box" style="color: #38bdf8;">🛣️</div>
                <div class="btn-text">
                    <span class="btn-title">6. SR GPS Route Tracking</span>
                    <span class="btn-desc">Multi-SR Journeys, Overlaps & Backtracking</span>
                </div>
            </button>

            <button class="nav-map-btn" id="btn-mode-7" onclick="switchMapMode(7)">
                <div class="icon-box" style="color: #ec4899;">🚩</div>
                <div class="btn-text">
                    <span class="btn-title">7. High-Visit Zero-Order Flaws</span>
                    <span class="btn-desc">Route Planning Inefficiencies & Conversion Failures</span>
                </div>
            </button>

            <div class="diagnostic-card" id="mode-desc-card">
                <div class="diagnostic-header" id="mode-desc-title">Framework 1 Active</div>
                <div class="diagnostic-body" id="mode-desc-body">
                    Plotting Nationwide Registered Outlets vs Active Stores that placed revenue orders. Green represents active commercial partners, Amber represents registered unsold stores.
                </div>
            </div>

            <div class="sidebar-section-title">Quick Region Focus</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                <button class="nav-map-btn" style="padding: 8px 10px; font-size:12px;" onclick="zoomTo(23.8103, 90.4125, 12)">Dhaka</button>
                <button class="nav-map-btn" style="padding: 8px 10px; font-size:12px;" onclick="zoomTo(22.3569, 91.7832, 12)">Chattogram</button>
                <button class="nav-map-btn" style="padding: 8px 10px; font-size:12px;" onclick="zoomTo(24.3636, 88.6241, 12)">Rajshahi</button>
                <button class="nav-map-btn" style="padding: 8px 10px; font-size:12px;" onclick="zoomTo(24.8949, 91.8687, 12)">Sylhet</button>
            </div>
        </div>

        <div id="map"></div>
    </div>

    <script>
        const DATA = {suite_json};

        // Initialize Base Map
        const map = L.map('map', {{
            center: [23.6850, 90.3563],
            zoom: 7,
            zoomControl: true
        }});

        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; CartoDB & Sokrio Data Science',
            maxZoom: 19
        }}).addTo(map);

        // Map Layers Container
        let currentLayer = null;

        function clearCurrentLayer() {{
            if (currentLayer) {{
                map.removeLayer(currentLayer);
                currentLayer = null;
            }}
        }}

        // Mode 1: Nationwide Retail Footprint
        function renderMode1() {{
            const cluster = L.markerClusterGroup({{ chunkedLoading: true, maxClusterRadius: 40 }});
            DATA.footprint.forEach(o => {{
                const isActive = o.footprint_status.includes("Active");
                const color = isActive ? '#10b981' : '#f59e0b';
                const marker = L.circleMarker([o.lat, o.long], {{
                    radius: isActive ? 6 : 4,
                    fillColor: color,
                    color: '#ffffff',
                    weight: 0.8,
                    fillOpacity: 0.85
                }});
                marker.bindPopup(`
                    <div class="pop-title">${{o.outlet_name || 'Retail Outlet'}}</div>
                    <div class="pop-row"><span class="pop-label">Territory:</span><span class="pop-val">#${{o.territory_id}}</span></div>
                    <div class="pop-row"><span class="pop-label">Footprint Status:</span><span class="pop-val" style="color:${{color}};">${{o.footprint_status}}</span></div>
                    <div class="pop-row"><span class="pop-label">Revenue (BDT):</span><span class="pop-val">BDT ${{Number(o.total_revenue).toLocaleString()}}</span></div>
                    <div class="pop-row"><span class="pop-label">Total Orders:</span><span class="pop-val">${{o.total_orders}}</span></div>
                `);
                cluster.addLayer(marker);
            }});
            currentLayer = cluster;
            map.addLayer(currentLayer);
        }}

        // Mode 2: Visit Density & Heatmap
        function renderMode2() {{
            const group = L.layerGroup();
            const pts = DATA.heat_points.map(p => [p.lat, p.long, Math.min(1.0, p.total_visits / 8 + 0.2)]);
            const heat = L.heatLayer(pts, {{
                radius: 22,
                blur: 16,
                maxZoom: 14,
                gradient: {{ 0.2: '#00f2fe', 0.4: '#10b981', 0.7: '#f59e0b', 1.0: '#ef4444' }}
            }});
            group.addLayer(heat);

            // Add Top Micro-Hub overlay
            DATA.micro_hubs.slice(0, 50).forEach((hub, idx) => {{
                const c = L.circleMarker([hub.lat_grid, hub.long_grid], {{
                    radius: 12,
                    fillColor: '#ef4444',
                    color: '#fff',
                    weight: 2,
                    fillOpacity: 0.8
                }});
                c.bindPopup(`
                    <div class="pop-title">🔥 Top Micro-Hub #${{idx+1}}</div>
                    <div class="pop-row"><span class="pop-label">Stores in Hub:</span><span class="pop-val">${{hub.outlet_count}} Outlets</span></div>
                    <div class="pop-row"><span class="pop-label">Hub Visits:</span><span class="pop-val">${{hub.hub_visits}} Visits</span></div>
                    <div class="pop-row"><span class="pop-label">Total Sales:</span><span class="pop-val" style="color:#00f2fe;">BDT ${{Number(hub.hub_revenue).toLocaleString()}}</span></div>
                `);
                group.addLayer(c);
            }});
            currentLayer = group;
            map.addLayer(currentLayer);
        }}

        // Mode 3: Operational Blind Spots
        function renderMode3() {{
            const cluster = L.markerClusterGroup({{ chunkedLoading: true, maxClusterRadius: 40 }});
            DATA.blind_spots.forEach(o => {{
                const marker = L.circleMarker([o.lat, o.long], {{
                    radius: 5,
                    fillColor: '#ef4444',
                    color: '#fff',
                    weight: 1,
                    fillOpacity: 0.9
                }});
                marker.bindPopup(`
                    <div class="pop-title">⚠️ Operational Blind Spot</div>
                    <div class="pop-row"><span class="pop-label">Outlet Name:</span><span class="pop-val">${{o.outlet_name || 'N/A'}}</span></div>
                    <div class="pop-row"><span class="pop-label">Territory ID:</span><span class="pop-val">#${{o.territory_id}}</span></div>
                    <div class="pop-row"><span class="pop-label">Address:</span><span class="pop-val">${{o.address || 'Field Registered Store'}}</span></div>
                    <div class="pop-row"><span class="pop-label">Audit Status:</span><span class="pop-val" style="color:#ef4444;">ZERO Visits Logged</span></div>
                `);
                cluster.addLayer(marker);
            }});
            currentLayer = cluster;
            map.addLayer(currentLayer);
        }}

        // Mode 4: White Space Expansion Opportunities
        function renderMode4() {{
            const group = L.layerGroup();
            DATA.white_space.forEach((ws, idx) => {{
                const radius = Math.min(30, Math.max(12, Math.sqrt(ws.total_regional_stores) * 1.5));
                const circle = L.circleMarker([ws.lat_region, ws.long_region], {{
                    radius: radius,
                    fillColor: '#a855f7',
                    color: '#ffffff',
                    weight: 2,
                    fillOpacity: 0.7
                }});
                circle.bindPopup(`
                    <div class="pop-title">🚀 White Space Cluster #${{idx+1}}</div>
                    <div class="pop-row"><span class="pop-label">Regional Outlets:</span><span class="pop-val">${{ws.total_regional_stores}}</span></div>
                    <div class="pop-row"><span class="pop-label">Unserved Blind Ratio:</span><span class="pop-val" style="color:#f59e0b;">${{ws.unvisited_pct}}% Unvisited</span></div>
                    <div class="pop-row"><span class="pop-label">Existing Revenue:</span><span class="pop-val">BDT ${{Number(ws.regional_revenue).toLocaleString()}}</span></div>
                    <div class="pop-row"><span class="pop-label">Expansion Action:</span><span class="pop-val" style="color:#a855f7;">Deploy New SR Sub-Route</span></div>
                `);
                group.addLayer(circle);
            }});
            currentLayer = group;
            map.addLayer(currentLayer);
        }}

        // Mode 5: 3D Sales Height Visualization
        function renderMode5() {{
            const group = L.layerGroup();
            DATA.pillars_3d.forEach(p => {{
                const heightPx = Math.min(80, Math.max(15, Math.log10(p.total_revenue) * 14));
                const customIcon = L.divIcon({{
                    className: 'pillar-icon',
                    html: `<div class="pillar-bar" style="height:${{heightPx}}px;"></div>`,
                    iconSize: [12, heightPx],
                    iconAnchor: [6, heightPx]
                }});
                const marker = L.marker([p.lat, p.long], {{ icon: customIcon }});
                marker.bindPopup(`
                    <div class="pop-title">📊 3D Sales Height Pillar</div>
                    <div class="pop-row"><span class="pop-label">Store:</span><span class="pop-val">${{p.outlet_name}}</span></div>
                    <div class="pop-row"><span class="pop-label">Sales Revenue:</span><span class="pop-val" style="color:#00f2fe;">BDT ${{Number(p.total_revenue).toLocaleString()}}</span></div>
                    <div class="pop-row"><span class="pop-label">Tier:</span><span class="pop-val">${{p.tier}}</span></div>
                    <div class="pop-row"><span class="pop-label">Pillar Height:</span><span class="pop-val">${{Math.round(heightPx)}}px Volume Index</span></div>
                `);
                group.addLayer(marker);
            }});
            currentLayer = group;
            map.addLayer(currentLayer);
        }}

        // Mode 6: SR GPS Journey & Route Paths
        function renderMode6() {{
            const group = L.layerGroup();
            const colors = ['#00f2fe', '#10b981', '#f59e0b', '#ec4899', '#38bdf8', '#a855f7', '#fbbf24', '#f43f5e'];
            DATA.sr_routes.forEach((route, idx) => {{
                const c = colors[idx % colors.length];
                const latlngs = route.points.map(pt => [pt.lat, pt.lng]);
                
                // Polyline path
                const line = L.polyline(latlngs, {{
                    color: c,
                    weight: 3.5,
                    opacity: 0.85,
                    dashArray: '5, 8'
                }});
                line.bindPopup(`
                    <div class="pop-title">🛣️ ${{route.sr_id}} Journey Route</div>
                    <div class="pop-row"><span class="pop-label">Waypoints Logged:</span><span class="pop-val">${{route.waypoints}} Check-ins</span></div>
                    <div class="pop-row"><span class="pop-label">Diagnosis:</span><span class="pop-val">Route Zigzag & Overlap Analyzed</span></div>
                `);
                group.addLayer(line);

                // Start and End Pins
                if (latlngs.length > 0) {{
                    const startPin = L.circleMarker(latlngs[0], {{ radius: 6, fillColor: '#10b981', color: '#fff', weight: 2, fillOpacity: 1 }});
                    startPin.bindPopup(`<b>${{route.sr_id}} Start Point</b>`);
                    group.addLayer(startPin);

                    const endPin = L.circleMarker(latlngs[latlngs.length-1], {{ radius: 6, fillColor: '#ef4444', color: '#fff', weight: 2, fillOpacity: 1 }});
                    endPin.bindPopup(`<b>${{route.sr_id}} Last Check-in</b>`);
                    group.addLayer(endPin);
                }}
            }});
            currentLayer = group;
            map.addLayer(currentLayer);
        }}

        // Mode 7: High-Value Non-Ordered Outlets
        function renderMode7() {{
            const cluster = L.markerClusterGroup({{ chunkedLoading: true, maxClusterRadius: 35 }});
            DATA.high_visit_zero_order.forEach(o => {{
                const marker = L.circleMarker([o.lat, o.long], {{
                    radius: 7,
                    fillColor: '#ec4899',
                    color: '#fff',
                    weight: 1.5,
                    fillOpacity: 0.9
                }});
                marker.bindPopup(`
                    <div class="pop-title">🚩 Conversion Failure Audit</div>
                    <div class="pop-row"><span class="pop-label">Outlet:</span><span class="pop-val">${{o.outlet_name || 'Outlet Store'}}</span></div>
                    <div class="pop-row"><span class="pop-label">Territory:</span><span class="pop-val">#${{o.territory_id}}</span></div>
                    <div class="pop-row"><span class="pop-label">Assigned SR:</span><span class="pop-val">SR #${{o.sr_id}}</span></div>
                    <div class="pop-row"><span class="pop-label">Wasted Visits:</span><span class="pop-val" style="color:#ef4444;">${{o.total_visits}} Physical Visits</span></div>
                    <div class="pop-row"><span class="pop-label">Conversion:</span><span class="pop-val" style="color:#ef4444;">0 Orders (0 BDT)</span></div>
                    <div class="pop-row"><span class="pop-label">Action:</span><span class="pop-val">Reassign SR / Review Stock & Credit</span></div>
                `);
                cluster.addLayer(marker);
            }});
            currentLayer = cluster;
            map.addLayer(currentLayer);
        }}

        // Mode Switching Logic
        const modeDescriptions = {{
            1: {{
                title: "1. Nationwide Retail Footprint",
                body: "Plotting Nationwide Registered Outlets vs Active Stores that placed revenue orders. Green represents active commercial partners, Amber represents registered unsold stores."
            }},
            2: {{
                title: "2. Visit Density & Heatmap",
                body: "Operational intensity heatmap visualizing 1.57 Million field visits. Color gradients illustrate Green (Regular Coverage) to Red (High-Density Top Micro-Hubs)."
            }},
            3: {{
                title: "3. Operational Blind Spots & Accountability",
                body: "Precision mapping of 73,453 unvisited outlets (26.03% of universe) with zero SR check-ins over the 4-month cycle, linked to territory accountability."
            }},
            4: {{
                title: "4. White Space & Expansion Opportunity",
                body: "Identifies regional clusters where high store counts exist alongside extreme unvisited ratios (>35%), highlighting prime targets for sub-distributor expansion."
            }},
            5: {{
                title: "5. 3D Sales Height Visualization",
                body: "Sales volume represented as extruded 3D height pillars. Contrasts mega-tier platinum outlets against low-volume retail clusters geographically."
            }},
            6: {{
                title: "6. SR GPS Route Path & Journey Tracking",
                body: "Visualizes actual SR GPS travel paths across field visits, diagnosing route zigzagging, distance discrepancies, and backtracking inefficiencies."
            }},
            7: {{
                title: "7. High-Visit Zero-Order Flaws",
                body: "Isolates outlets visited 3 to 15+ times by SRs with absolute ZERO order conversion, exposing major route-planning flaws and pitching gaps."
            }}
        }};

        function switchMapMode(modeNum) {{
            // Update active button
            for (let i = 1; i <= 7; i++) {{
                const btn = document.getElementById('btn-mode-' + i);
                if (btn) btn.classList.toggle('active', i === modeNum);
            }}

            // Update description box
            document.getElementById('mode-desc-title').innerText = modeDescriptions[modeNum].title;
            document.getElementById('mode-desc-body').innerText = modeDescriptions[modeNum].body;

            // Clear previous layer and render selected
            clearCurrentLayer();
            if (modeNum === 1) renderMode1();
            else if (modeNum === 2) renderMode2();
            else if (modeNum === 3) renderMode3();
            else if (modeNum === 4) renderMode4();
            else if (modeNum === 5) renderMode5();
            else if (modeNum === 6) renderMode6();
            else if (modeNum === 7) renderMode7();
        }}

        function zoomTo(lat, lng, zoomLevel) {{
            map.flyTo([lat, lng], zoomLevel, {{ duration: 1.2 }});
        }}

        // Default Load Mode 1
        renderMode1();
    </script>
</body>
</html>
"""

with open(r"E:\ITL FINAL ADV ANALYSIS\geo_intelligence_explorer.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Updated Complete 7-in-1 Suite in geo_intelligence_explorer.html successfully!")
