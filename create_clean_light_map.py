import json

with open(r"E:\ITL FINAL ADV ANALYSIS\module1_full_suite_data.json", "r", encoding="utf-8") as f:
    suite_json = f.read()

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Geo-Intelligence Explorer™ - Sokrio Technologies</title>
    <!-- Leaflet & Extensions -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.js"></script>
    <script src="https://unpkg.com/leaflet-heat@0.2.0/dist/leaflet-heat.js"></script>
    <style>
        :root {{
            --bg-body: #f8fafc;
            --sidebar-bg: #ffffff;
            --card-bg: #ffffff;
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --accent-cyan: #0284c7;
            --accent-green: #059669;
            --accent-amber: #d97706;
            --accent-red: #dc2626;
            --accent-purple: #7c3aed;
            --text-dark: #0f172a;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}
        body {{
            background: var(--bg-body);
            color: var(--text-dark);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        /* Header */
        header {{
            height: 70px;
            background: #ffffff;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 28px;
            z-index: 1000;
            box-shadow: var(--shadow-sm);
        }}
        .brand-section {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .brand-badge {{
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: #ffffff;
            font-weight: 800;
            font-size: 12px;
            padding: 5px 12px;
            border-radius: 6px;
            letter-spacing: 0.8px;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
        }}
        .brand-title {{
            font-size: 18px;
            font-weight: 800;
            color: #0f172a;
        }}
        .brand-subtitle {{
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 500;
        }}
        .header-stats {{
            display: flex;
            gap: 14px;
        }}
        .stat-card {{
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 6px 14px;
            display: flex;
            flex-direction: column;
        }}
        .stat-card .label {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            font-weight: 600;
        }}
        .stat-card .val {{
            font-size: 14px;
            font-weight: 800;
            color: #0f172a;
        }}
        /* Workspace */
        .workspace {{
            display: flex;
            flex: 1;
            position: relative;
            overflow: hidden;
        }}
        /* Sidebar */
        .sidebar {{
            width: 380px;
            background: var(--sidebar-bg);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            padding: 20px;
            gap: 14px;
            overflow-y: auto;
            z-index: 999;
            box-shadow: 2px 0 10px rgba(0,0,0,0.02);
        }}
        .sidebar-heading {{
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-muted);
            margin-bottom: 2px;
        }}
        .map-mode-btn {{
            width: 100%;
            background: #ffffff;
            border: 1.5px solid var(--border);
            border-radius: 12px;
            padding: 12px 14px;
            text-align: left;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .map-mode-btn:hover {{
            border-color: #93c5fd;
            background: #f8fafc;
            transform: translateY(-1px);
            box-shadow: var(--shadow-sm);
        }}
        .map-mode-btn.active {{
            background: #eff6ff;
            border-color: #2563eb;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.12);
        }}
        .btn-icon {{
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 17px;
            background: #f1f5f9;
            flex-shrink: 0;
        }}
        .map-mode-btn.active .btn-icon {{
            background: #dbeafe;
            color: #1d4ed8;
        }}
        .btn-details {{
            display: flex;
            flex-direction: column;
            flex: 1;
        }}
        .btn-title {{
            font-size: 13px;
            font-weight: 700;
            color: #1e293b;
        }}
        .map-mode-btn.active .btn-title {{
            color: #1d4ed8;
        }}
        .btn-desc {{
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 2px;
        }}
        /* Diagnostic Info Card */
        .info-card {{
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px 16px;
        }}
        .info-title {{
            font-size: 12px;
            font-weight: 800;
            color: #1e293b;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .info-body {{
            font-size: 12px;
            line-height: 1.55;
            color: #475569;
        }}
        /* Basemap Selector */
        .basemap-toggle {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }}
        .base-btn {{
            padding: 7px 10px;
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 11px;
            font-weight: 600;
            color: #475569;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .base-btn.active {{
            background: #0f172a;
            color: #ffffff;
            border-color: #0f172a;
        }}
        /* Map Canvas */
        #map {{
            flex: 1;
            height: 100%;
            background: #e2e8f0;
        }}
        /* Leaflet Popups Clean Light Theme */
        .leaflet-popup-content-wrapper {{
            background: #ffffff !important;
            color: #0f172a !important;
            border-radius: 14px !important;
            box-shadow: 0 14px 28px rgba(0,0,0,0.12), 0 10px 10px rgba(0,0,0,0.06) !important;
            border: 1px solid #e2e8f0 !important;
            padding: 4px !important;
        }}
        .leaflet-popup-tip {{
            background: #ffffff !important;
        }}
        .pop-header {{
            font-size: 14px;
            font-weight: 800;
            color: #0f172a;
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 6px;
            margin-bottom: 8px;
        }}
        .pop-row {{
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            margin-bottom: 5px;
            gap: 16px;
        }}
        .pop-lbl {{
            color: #64748b;
            font-weight: 500;
        }}
        .pop-val {{
            font-weight: 700;
            color: #0f172a;
        }}
        /* 3D Pillar Style */
        .pillar-icon {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-end;
        }}
        .pillar-bar {{
            width: 10px;
            background: linear-gradient(to top, #2563eb, #38bdf8);
            border-radius: 4px 4px 0 0;
            box-shadow: 0 4px 8px rgba(37,99,235,0.4);
            border: 1px solid #ffffff;
        }}
        /* Custom Marker Cluster Styling (Light Theme) */
        .marker-cluster-small {{
            background-color: rgba(16, 185, 129, 0.4) !important;
        }}
        .marker-cluster-small div {{
            background-color: #10b981 !important;
            color: #ffffff !important;
            font-weight: 700 !important;
        }}
        .marker-cluster-medium {{
            background-color: rgba(245, 158, 11, 0.4) !important;
        }}
        .marker-cluster-medium div {{
            background-color: #f59e0b !important;
            color: #ffffff !important;
            font-weight: 700 !important;
        }}
        .marker-cluster-large {{
            background-color: rgba(37, 99, 235, 0.4) !important;
        }}
        .marker-cluster-large div {{
            background-color: #2563eb !important;
            color: #ffffff !important;
            font-weight: 700 !important;
        }}
    </style>
</head>
<body>
    <header>
        <div class="brand-section">
            <span class="brand-badge">SOKRIO</span>
            <div>
                <div class="brand-title">Geo-Intelligence Explorer™</div>
                <div class="brand-subtitle">Executive Geospatial Analytics & Territory Intelligence Suite</div>
            </div>
        </div>
        <div class="header-stats">
            <div class="stat-card">
                <span class="label">Total Outlets</span>
                <span class="val">282,171 Stores</span>
            </div>
            <div class="stat-card">
                <span class="label">Active Buyers</span>
                <span class="val" style="color: var(--accent-green);">208,831 (74.0%)</span>
            </div>
            <div class="stat-card">
                <span class="label">Blind Spots</span>
                <span class="val" style="color: var(--accent-red);">73,453 (26.0%)</span>
            </div>
            <div class="stat-card">
                <span class="label">Total Net Revenue</span>
                <span class="val" style="color: var(--primary);">BDT 475.92 Cr</span>
            </div>
        </div>
    </header>

    <div class="workspace">
        <div class="sidebar">
            <div class="sidebar-heading">Select Diagnostic Map Module (1 - 7)</div>

            <button class="map-mode-btn active" id="btn-m-1" onclick="switchMode(1)">
                <div class="btn-icon">🌐</div>
                <div class="btn-details">
                    <span class="btn-title">1. Nationwide Retail Footprint</span>
                    <span class="btn-desc">Registered vs Active Stores across Bangladesh</span>
                </div>
            </button>

            <button class="map-mode-btn" id="btn-m-2" onclick="switchMode(2)">
                <div class="btn-icon">🔥</div>
                <div class="btn-details">
                    <span class="btn-title">2. Visit Density & Heatmap</span>
                    <span class="btn-desc">1.57M Visits & Top 300 High-Density Micro-Hubs</span>
                </div>
            </button>

            <button class="map-mode-btn" id="btn-m-3" onclick="switchMode(3)">
                <div class="btn-icon">⚠️</div>
                <div class="btn-details">
                    <span class="btn-title">3. Operational Blind Spots</span>
                    <span class="btn-desc">73,453 Unvisited Outlets & SR Accountability</span>
                </div>
            </button>

            <button class="map-mode-btn" id="btn-m-4" onclick="switchMode(4)">
                <div class="btn-icon">🚀</div>
                <div class="btn-details">
                    <span class="btn-title">4. White Space & Expansion</span>
                    <span class="btn-desc">High Potential Underserved Market Clusters</span>
                </div>
            </button>

            <button class="map-mode-btn" id="btn-m-5" onclick="switchMode(5)">
                <div class="btn-icon">📊</div>
                <div class="btn-details">
                    <span class="btn-title">5. 3D Sales Height & Tiering</span>
                    <span class="btn-desc">Extruded Volume Pillars & High-Value Clusters</span>
                </div>
            </button>

            <button class="map-mode-btn" id="btn-m-6" onclick="switchMode(6)">
                <div class="btn-icon">🛣️</div>
                <div class="btn-details">
                    <span class="btn-title">6. SR GPS Route Tracking</span>
                    <span class="btn-desc">SR Journeys, Overlaps & Route Inefficiencies</span>
                </div>
            </button>

            <button class="map-mode-btn" id="btn-m-7" onclick="switchMode(7)">
                <div class="btn-icon">🚩</div>
                <div class="btn-details">
                    <span class="btn-title">7. High-Visit Zero-Order Flaws</span>
                    <span class="btn-desc">Zero-Conversion Stores & Route Planning Flaws</span>
                </div>
            </button>

            <div class="info-card">
                <div class="info-title" id="info-card-title">💡 Active Framework Diagnostics</div>
                <div class="info-body" id="info-card-desc">
                    Plotting Nationwide Registered Outlets vs Active Stores that placed revenue orders. Green points denote commercial buyers, Orange points represent registered unsold stores.
                </div>
            </div>

            <div class="sidebar-heading">Map Style & Quick Zoom</div>
            <div class="basemap-toggle">
                <button class="base-btn active" id="btn-base-osm" onclick="setBaseMap('osm')">Clean Streets</button>
                <button class="base-btn" id="btn-base-light" onclick="setBaseMap('light')">Positron Light</button>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 4px;">
                <button class="base-btn" onclick="zoomTo(23.8103, 90.4125, 12)">Dhaka Metro</button>
                <button class="base-btn" onclick="zoomTo(22.3569, 91.7832, 12)">Chattogram</button>
                <button class="base-btn" onclick="zoomTo(24.3636, 88.6241, 12)">Rajshahi</button>
                <button class="base-btn" onclick="zoomTo(24.8949, 91.8687, 12)">Sylhet</button>
            </div>
        </div>

        <div id="map"></div>
    </div>

    <script>
        const DATA = {suite_json};

        // Initialize Map
        const map = L.map('map', {{
            center: [23.6850, 90.3563],
            zoom: 7,
            zoomControl: true
        }});

        // Clean Free Basemap Layers (No API Key Required & No Watermarks)
        const osmLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        }});

        const lightLayer = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap & CARTO'
        }});

        // Default basemap: Clean OpenStreetMap Streets
        osmLayer.addTo(map);
        let activeBase = 'osm';

        function setBaseMap(style) {{
            if (style === 'osm') {{
                map.removeLayer(lightLayer);
                map.addLayer(osmLayer);
                document.getElementById('btn-base-osm').classList.add('active');
                document.getElementById('btn-base-light').classList.remove('active');
            }} else {{
                map.removeLayer(osmLayer);
                map.addLayer(lightLayer);
                document.getElementById('btn-base-light').classList.add('active');
                document.getElementById('btn-base-osm').classList.remove('active');
            }}
        }}

        // Layer Management
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
                const color = isActive ? '#059669' : '#d97706';
                const marker = L.circleMarker([o.lat, o.long], {{
                    radius: isActive ? 6 : 4.5,
                    fillColor: color,
                    color: '#ffffff',
                    weight: 1.2,
                    fillOpacity: 0.9
                }});
                marker.bindPopup(`
                    <div class="pop-header">${{o.outlet_name || 'Retail Outlet'}}</div>
                    <div class="pop-row"><span class="pop-lbl">Territory ID:</span><span class="pop-val">#${{o.territory_id}}</span></div>
                    <div class="pop-row"><span class="pop-lbl">Status:</span><span class="pop-val" style="color:${{color}};">${{o.footprint_status}}</span></div>
                    <div class="pop-row"><span class="pop-lbl">Sales Revenue:</span><span class="pop-val" style="color:#2563eb;">BDT ${{Number(o.total_revenue).toLocaleString()}}</span></div>
                    <div class="pop-row"><span class="pop-lbl">Orders:</span><span class="pop-val">${{o.total_orders}}</span></div>
                `);
                cluster.addLayer(marker);
            }});
            currentLayer = cluster;
            map.addLayer(currentLayer);
        }}

        // Mode 2: Visit Density Heatmap & Top 300 Micro-Hubs
        function renderMode2() {{
            const group = L.layerGroup();
            const pts = DATA.heat_points.map(p => [p.lat, p.long, Math.min(1.0, p.total_visits / 8 + 0.2)]);
            const heat = L.heatLayer(pts, {{
                radius: 20,
                blur: 15,
                maxZoom: 14,
                gradient: {{ 0.2: '#38bdf8', 0.5: '#10b981', 0.8: '#f59e0b', 1.0: '#dc2626' }}
            }});
            group.addLayer(heat);

            // Add Top 300 Micro-Hub Circles
            DATA.micro_hubs.slice(0, 100).forEach((hub, idx) => {{
                const c = L.circleMarker([hub.lat_grid, hub.long_grid], {{
                    radius: Math.min(22, Math.max(9, Math.sqrt(hub.outlet_count) * 2.2)),
                    fillColor: '#dc2626',
                    color: '#ffffff',
                    weight: 2,
                    fillOpacity: 0.75
                }});
                c.bindPopup(`
                    <div class="pop-header">🔥 Top Micro-Hub #${{idx+1}}</div>
                    <div class="pop-row"><span class="pop-lbl">Density:</span><span class="pop-val">${{hub.outlet_count}} Outlets in Cluster</span></div>
                    <div class="pop-row"><span class="pop-lbl">Visits Recorded:</span><span class="pop-val">${{hub.hub_visits}} Visits</span></div>
                    <div class="pop-row"><span class="pop-lbl">Total Sales:</span><span class="pop-val" style="color:#2563eb;">BDT ${{Number(hub.hub_revenue).toLocaleString()}}</span></div>
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
                    radius: 5.5,
                    fillColor: '#dc2626',
                    color: '#ffffff',
                    weight: 1.2,
                    fillOpacity: 0.95
                }});
                marker.bindPopup(`
                    <div class="pop-header" style="color:#dc2626;">⚠️ Operational Blind Spot</div>
                    <div class="pop-row"><span class="pop-lbl">Store Name:</span><span class="pop-val">${{o.outlet_name || 'N/A'}}</span></div>
                    <div class="pop-row"><span class="pop-lbl">Territory ID:</span><span class="pop-val">#${{o.territory_id}}</span></div>
                    <div class="pop-row"><span class="pop-lbl">Address:</span><span class="pop-val">${{o.address || 'Field Registered Store'}}</span></div>
                    <div class="pop-row"><span class="pop-lbl">Audit Result:</span><span class="pop-val" style="color:#dc2626;">ZERO SR Visits in 4 Months</span></div>
                `);
                cluster.addLayer(marker);
            }});
            currentLayer = cluster;
            map.addLayer(currentLayer);
        }}

        // Mode 4: White Space Expansion
        function renderMode4() {{
            const group = L.layerGroup();
            DATA.white_space.forEach((ws, idx) => {{
                const radius = Math.min(28, Math.max(12, Math.sqrt(ws.total_regional_stores) * 1.4));
                const circle = L.circleMarker([ws.lat_region, ws.long_region], {{
                    radius: radius,
                    fillColor: '#7c3aed',
                    color: '#ffffff',
                    weight: 2,
                    fillOpacity: 0.8
                }});
                circle.bindPopup(`
                    <div class="pop-header" style="color:#7c3aed;">🚀 White Space Cluster #${{idx+1}}</div>
                    <div class="pop-row"><span class="pop-lbl">Regional Stores:</span><span class="pop-val">${{ws.total_regional_stores}}</span></div>
                    <div class="pop-row"><span class="pop-lbl">Unserved Ratio:</span><span class="pop-val" style="color:#d97706;">${{ws.unvisited_pct}}% Unvisited</span></div>
                    <div class="pop-row"><span class="pop-lbl">Existing Sales:</span><span class="pop-val">BDT ${{Number(ws.regional_revenue).toLocaleString()}}</span></div>
                    <div class="pop-row"><span class="pop-lbl">Opportunity:</span><span class="pop-val" style="color:#7c3aed;">Deploy Sub-Distributor / SR Route</span></div>
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
                const heightPx = Math.min(75, Math.max(16, Math.log10(p.total_revenue) * 13));
                const customIcon = L.divIcon({{
                    className: 'pillar-icon',
                    html: `<div class="pillar-bar" style="height:${{heightPx}}px;"></div>`,
                    iconSize: [12, heightPx],
                    iconAnchor: [6, heightPx]
                }});
                const marker = L.marker([p.lat, p.long], {{ icon: customIcon }});
                marker.bindPopup(`
                    <div class="pop-header">📊 3D Volume Pillar</div>
                    <div class="pop-row"><span class="pop-lbl">Store Name:</span><span class="pop-val">${{p.outlet_name}}</span></div>
                    <div class="pop-row"><span class="pop-lbl">Net Sales:</span><span class="pop-val" style="color:#2563eb;">BDT ${{Number(p.total_revenue).toLocaleString()}}</span></div>
                    <div class="pop-row"><span class="pop-lbl">Tier:</span><span class="pop-val">${{p.tier}}</span></div>
                    <div class="pop-row"><span class="pop-lbl">Pillar Height Index:</span><span class="pop-val">${{Math.round(heightPx)}}px</span></div>
                `);
                group.addLayer(marker);
            }});
            currentLayer = group;
            map.addLayer(currentLayer);
        }}

        // Mode 6: SR GPS Journey & Route Paths
        function renderMode6() {{
            const group = L.layerGroup();
            const colors = ['#2563eb', '#059669', '#d97706', '#dc2626', '#7c3aed', '#0284c7', '#ec4899', '#10b981'];
            DATA.sr_routes.forEach((route, idx) => {{
                const c = colors[idx % colors.length];
                const latlngs = route.points.map(pt => [pt.lat, pt.lng]);
                
                const line = L.polyline(latlngs, {{
                    color: c,
                    weight: 3.5,
                    opacity: 0.9,
                    dashArray: '4, 6'
                }});
                line.bindPopup(`
                    <div class="pop-header">🛣️ ${{route.sr_id}} Journey Path</div>
                    <div class="pop-row"><span class="pop-lbl">Logged Check-ins:</span><span class="pop-val">${{route.waypoints}} Points</span></div>
                    <div class="pop-row"><span class="pop-lbl">Route Diagnostic:</span><span class="pop-val">Backtracking & Travel Inefficiency Logged</span></div>
                `);
                group.addLayer(line);

                if (latlngs.length > 0) {{
                    const startMarker = L.circleMarker(latlngs[0], {{ radius: 6, fillColor: '#059669', color: '#fff', weight: 2, fillOpacity: 1 }});
                    startMarker.bindPopup(`<b>${{route.sr_id}} Route Start</b>`);
                    group.addLayer(startMarker);

                    const endMarker = L.circleMarker(latlngs[latlngs.length-1], {{ radius: 6, fillColor: '#dc2626', color: '#fff', weight: 2, fillOpacity: 1 }});
                    endMarker.bindPopup(`<b>${{route.sr_id}} Last Check-in</b>`);
                    group.addLayer(endMarker);
                }}
            }});
            currentLayer = group;
            map.addLayer(currentLayer);
        }}

        // Mode 7: High-Visit Zero-Order Flaws
        function renderMode7() {{
            const cluster = L.markerClusterGroup({{ chunkedLoading: true, maxClusterRadius: 35 }});
            DATA.high_visit_zero_order.forEach(o => {{
                const marker = L.circleMarker([o.lat, o.long], {{
                    radius: 7,
                    fillColor: '#ec4899',
                    color: '#ffffff',
                    weight: 1.5,
                    fillOpacity: 0.95
                }});
                marker.bindPopup(`
                    <div class="pop-header" style="color:#ec4899;">🚩 Conversion Failure Audit</div>
                    <div class="pop-row"><span class="pop-lbl">Store Name:</span><span class="pop-val">${{o.outlet_name || 'Outlet Store'}}</span></div>
                    <div class="pop-row"><span class="pop-lbl">Territory ID:</span><span class="pop-val">#${{o.territory_id}}</span></div>
                    <div class="pop-row"><span class="pop-lbl">Assigned SR:</span><span class="pop-val">SR #${{o.sr_id}}</span></div>
                    <div class="pop-row"><span class="pop-lbl">Wasted Visits:</span><span class="pop-val" style="color:#dc2626;">${{o.total_visits}} Physical Visits</span></div>
                    <div class="pop-row"><span class="pop-lbl">Total Orders:</span><span class="pop-val" style="color:#dc2626;">0 Orders (0 BDT)</span></div>
                    <div class="pop-row"><span class="pop-lbl">Commercial Action:</span><span class="pop-val">Reallocate SR Time / Audit Credit</span></div>
                `);
                cluster.addLayer(marker);
            }});
            currentLayer = cluster;
            map.addLayer(currentLayer);
        }}

        // Descriptions
        const descriptions = {{
            1: {{
                title: "1. Nationwide Retail Footprint",
                desc: "Nationwide registered outlets vs active stores that generated revenue. Green points represent active ordering stores, orange points represent registered unsold stores."
            }},
            2: {{
                title: "2. Visit Density & Heatmap",
                desc: "Operational intensity heatmap analyzing 1.57 Million field check-ins. Red circles highlight the Top 300 high-density commercial micro-hubs."
            }},
            3: {{
                title: "3. Operational Blind Spots & Field Accountability",
                desc: "Precision mapping of 73,453 unvisited outlets (26.03% of total universe) with zero SR check-ins across 4 months, mapped directly to territory accountability."
            }},
            4: {{
                title: "4. White Space & Expansion Opportunity",
                desc: "Identifies regional retail clusters where high registered store density exists with high unvisited ratios (>35%), representing prime opportunities for expansion."
            }},
            5: {{
                title: "5. 3D Sales Height Visualization",
                desc: "Sales volume represented as vertical 3D height pillars, geographically contrasting high-performing Platinum outlets against standard retail clusters."
            }},
            6: {{
                title: "6. SR GPS Route Path & Journey Tracking",
                desc: "Visualizes actual GPS journey paths of SRs in the field, exposing route backtracking, zigzagging, and distance discrepancies."
            }},
            7: {{
                title: "7. High-Visit Zero-Order Route Flaws",
                desc: "Dedicated mapping of outlets visited 3 to 15+ times by SRs with 0% order conversion, pinpointing route planning flaws and pitching skill gaps."
            }}
        }};

        function switchMode(m) {{
            for (let i = 1; i <= 7; i++) {{
                const btn = document.getElementById('btn-m-' + i);
                if (btn) btn.classList.toggle('active', i === m);
            }}
            document.getElementById('info-card-title').innerText = descriptions[m].title;
            document.getElementById('info-card-desc').innerText = descriptions[m].desc;

            clearCurrentLayer();
            if (m === 1) renderMode1();
            else if (m === 2) renderMode2();
            else if (m === 3) renderMode3();
            else if (m === 4) renderMode4();
            else if (m === 5) renderMode5();
            else if (m === 6) renderMode6();
            else if (m === 7) renderMode7();
        }}

        function zoomTo(lat, lng, zoomLevel) {{
            map.flyTo([lat, lng], zoomLevel, {{ duration: 1.2 }});
        }}

        // Initial Load
        renderMode1();
    </script>
</body>
</html>
"""

with open(r"E:\ITL FINAL ADV ANALYSIS\geo_intelligence_explorer.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Clean Light-Themed Geo-Intelligence Explorer created successfully with zero API watermark!")
