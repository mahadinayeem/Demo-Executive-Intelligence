import json

with open(r"E:\ITL FINAL ADV ANALYSIS\map_data.json", "r", encoding="utf-8") as f:
    raw_json_str = f.read()

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Geo-Intelligence Explorer™ - Sokrio Technologies</title>
    <!-- Leaflet & Leaflet MarkerCluster -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
    <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
    <style>
        :root {{
            --bg-primary: #0b0f19;
            --bg-secondary: #131b2e;
            --card-bg: rgba(19, 27, 46, 0.88);
            --accent-cyan: #00f2fe;
            --accent-blue: #4facfe;
            --accent-green: #10b981;
            --accent-gold: #f59e0b;
            --accent-red: #ef4444;
            --accent-purple: #8b5cf6;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --border-glass: rgba(255, 255, 255, 0.12);
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        body {{
            background: var(--bg-primary);
            color: var(--text-main);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        /* Header */
        header {{
            height: 64px;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-glass);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            z-index: 1000;
        }}
        .logo-box {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .logo-badge {{
            background: linear-gradient(135deg, #00f2fe, #4facfe);
            color: #0b0f19;
            font-weight: 800;
            font-size: 13px;
            padding: 4px 8px;
            border-radius: 6px;
            letter-spacing: 1px;
        }}
        .brand-title {{
            font-size: 18px;
            font-weight: 700;
            background: linear-gradient(90deg, #fff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header-stats {{
            display: flex;
            align-items: center;
            gap: 24px;
        }}
        .stat-badge {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-glass);
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 12px;
            display: flex;
            flex-direction: column;
        }}
        .stat-badge span:first-child {{
            color: var(--text-muted);
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .stat-badge span:last-child {{
            font-weight: 700;
            font-size: 14px;
            color: var(--accent-cyan);
        }}
        /* Main Layout */
        .app-body {{
            display: flex;
            flex: 1;
            position: relative;
            overflow: hidden;
        }}
        /* Sidebar Controls */
        .sidebar {{
            width: 340px;
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border-right: 1px solid var(--border-glass);
            z-index: 999;
            display: flex;
            flex-direction: column;
            gap: 16px;
            padding: 20px;
            overflow-y: auto;
        }}
        .control-group {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            padding: 16px;
        }}
        .group-title {{
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--accent-cyan);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .layer-btn {{
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-glass);
            color: var(--text-main);
            padding: 10px 14px;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 8px;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        .layer-btn:hover {{
            background: rgba(255, 255, 255, 0.1);
            border-color: var(--accent-cyan);
        }}
        .layer-btn.active {{
            background: linear-gradient(135deg, rgba(0, 242, 254, 0.15), rgba(79, 172, 254, 0.15));
            border-color: var(--accent-cyan);
            box-shadow: 0 0 12px rgba(0, 242, 254, 0.25);
        }}
        .indicator-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 12px;
            margin-bottom: 8px;
            color: #d1d5db;
        }}
        /* Map Area */
        #map {{
            flex: 1;
            height: 100%;
            background: #090d16;
        }}
        /* Custom Tooltip / Popup */
        .custom-popup .leaflet-popup-content-wrapper {{
            background: var(--bg-secondary);
            color: var(--text-main);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            padding: 4px;
        }}
        .custom-popup .leaflet-popup-tip {{
            background: var(--bg-secondary);
        }}
        .popup-header {{
            font-size: 14px;
            font-weight: 700;
            color: var(--accent-cyan);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 6px;
            margin-bottom: 8px;
        }}
        .popup-row {{
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            margin-bottom: 4px;
            gap: 16px;
        }}
        .popup-label {{
            color: var(--text-muted);
        }}
        .popup-val {{
            font-weight: 600;
        }}
        /* Floating Info Box */
        .floating-info {{
            position: absolute;
            bottom: 24px;
            right: 24px;
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            padding: 16px 20px;
            z-index: 999;
            box-shadow: 0 12px 36px rgba(0,0,0,0.4);
            max-width: 320px;
        }}
        .floating-title {{
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 8px;
            color: var(--accent-cyan);
        }}
        .floating-text {{
            font-size: 12px;
            line-height: 1.5;
            color: var(--text-muted);
        }}
    </style>
</head>
<body>
    <header>
        <div class="logo-box">
            <span class="logo-badge">SOKRIO</span>
            <span class="brand-title">Geo-Intelligence Explorer™</span>
        </div>
        <div class="header-stats">
            <div class="stat-badge">
                <span>Total Master Stores</span>
                <span id="stat-outlets">282,171</span>
            </div>
            <div class="stat-badge">
                <span>Active Universe</span>
                <span id="stat-active" style="color: var(--accent-green);">208,831 (74.0%)</span>
            </div>
            <div class="stat-badge">
                <span>Blind Spots</span>
                <span id="stat-blind" style="color: var(--accent-red);">73,453 (26.0%)</span>
            </div>
            <div class="stat-badge">
                <span>Net Revenue</span>
                <span id="stat-rev" style="color: var(--accent-gold);">BDT 475.92 Cr</span>
            </div>
        </div>
    </header>

    <div class="app-body">
        <div class="sidebar">
            <div class="control-group">
                <div class="group-title">🎯 Diagnostic Map Layers</div>
                <button class="layer-btn active" id="btn-tiers" onclick="toggleLayer('tiers')">
                    <span>👑 Outlet Revenue Tiers</span>
                    <span class="indicator-dot" style="background: var(--accent-cyan);"></span>
                </button>
                <button class="layer-btn" id="btn-heatmap" onclick="toggleLayer('heatmap')">
                    <span>🔥 Visit Density Heatmap</span>
                    <span class="indicator-dot" style="background: #ff5722;"></span>
                </button>
                <button class="layer-btn" id="btn-microhubs" onclick="toggleLayer('microhubs')">
                    <span>🔴 Top 300 Micro-Hubs</span>
                    <span class="indicator-dot" style="background: var(--accent-red);"></span>
                </button>
                <button class="layer-btn" id="btn-blindspots" onclick="toggleLayer('blindspots')">
                    <span>⚠️ Operational Blind Spots</span>
                    <span class="indicator-dot" style="background: var(--accent-gold);"></span>
                </button>
                <button class="layer-btn" id="btn-redflags" onclick="toggleLayer('redflags')">
                    <span>🚩 Red Flag (0 Orders)</span>
                    <span class="indicator-dot" style="background: var(--accent-purple);"></span>
                </button>
                <button class="layer-btn" id="btn-routes" onclick="toggleLayer('routes')">
                    <span>🛣️ SR Journey Routes</span>
                    <span class="indicator-dot" style="background: #38bdf8;"></span>
                </button>
            </div>

            <div class="control-group">
                <div class="group-title">📊 Tier & Marker Legend</div>
                <div class="legend-item">
                    <span class="indicator-dot" style="background: #00f2fe; box-shadow: 0 0 8px #00f2fe;"></span>
                    <span>Tier 1: Platinum (> 100k BDT)</span>
                </div>
                <div class="legend-item">
                    <span class="indicator-dot" style="background: #10b981;"></span>
                    <span>Tier 2: Gold (30k - 100k BDT)</span>
                </div>
                <div class="legend-item">
                    <span class="indicator-dot" style="background: #3b82f6;"></span>
                    <span>Tier 3: Silver (10k - 30k BDT)</span>
                </div>
                <div class="legend-item">
                    <span class="indicator-dot" style="background: #f59e0b;"></span>
                    <span>Blind Spot (Zero SR Visits)</span>
                </div>
                <div class="legend-item">
                    <span class="indicator-dot" style="background: #ef4444;"></span>
                    <span>Red Flag (>=3 Visits, 0 Order)</span>
                </div>
            </div>

            <div class="control-group">
                <div class="group-title">⚡ Quick Zoom Presets</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <button class="layer-btn" style="margin-bottom:0;" onclick="zoomTo(23.8103, 90.4125, 12)">Dhaka Metro</button>
                    <button class="layer-btn" style="margin-bottom:0;" onclick="zoomTo(22.3569, 91.7832, 12)">Chattogram</button>
                    <button class="layer-btn" style="margin-bottom:0;" onclick="zoomTo(24.3636, 88.6241, 12)">Rajshahi</button>
                    <button class="layer-btn" style="margin-bottom:0;" onclick="zoomTo(24.8949, 91.8687, 12)">Sylhet</button>
                    <button class="layer-btn" style="margin-bottom:0;" onclick="zoomTo(22.7010, 90.3535, 12)">Barishal</button>
                    <button class="layer-btn" style="margin-bottom:0;" onclick="zoomTo(23.6850, 90.3563, 7)">All BD</button>
                </div>
            </div>
        </div>

        <div id="map"></div>

        <div class="floating-info">
            <div class="floating-title">Geo-Spatial Diagnostics Active</div>
            <div class="floating-text">
                Click any store or micro-hub bubble to inspect exact Sales Revenue, SR Visit Intensity, Order Count, and Blind Spot status.
            </div>
        </div>
    </div>

    <script>
        const MAP_DATA = {raw_json_str};

        // Initialize Leaflet Map
        const map = L.map('map', {{
            center: [23.6850, 90.3563],
            zoom: 7,
            zoomControl: true
        }});

        // Dark Luxury Tile Layer
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; CartoDB, OpenStreetMap & Sokrio Tech',
            maxZoom: 19
        }}).addTo(map);

        // Layer Groups
        const clusterGroup = L.markerClusterGroup({{
            chunkedLoading: true,
            maxClusterRadius: 45,
            spiderfyOnMaxZoom: true
        }});

        const heatLayerGroup = L.layerGroup();
        const microHubsGroup = L.layerGroup();
        const blindSpotsGroup = L.layerGroup();
        const redFlagsGroup = L.layerGroup();
        const routesGroup = L.layerGroup();

        // Color mapping
        function getMarkerColor(outlet) {{
            if (outlet.status_type.includes("Red Flag")) return '#ef4444';
            if (outlet.status_type.includes("Blind Spot")) return '#f59e0b';
            if (outlet.tier.includes("Tier 1")) return '#00f2fe';
            if (outlet.tier.includes("Tier 2")) return '#10b981';
            return '#3b82f6';
        }}

        // 1. Populate Outlets
        const heatPoints = [];
        MAP_DATA.outlets.forEach(o => {{
            if (!o.lat || !o.long) return;
            const color = getMarkerColor(o);
            heatPoints.push([o.lat, o.long, Math.min(1.0, o.total_visits / 10 + 0.1)]);

            const marker = L.circleMarker([o.lat, o.long], {{
                radius: o.tier.includes("Tier 1") ? 7 : 5,
                fillColor: color,
                color: '#fff',
                weight: 0.8,
                opacity: 0.9,
                fillOpacity: 0.85
            }});

            const popupContent = `
                <div class="popup-header">${{o.outlet_name || 'Outlet Store'}}</div>
                <div class="popup-row"><span class="popup-label">Territory:</span><span class="popup-val">#${{o.territory_id}}</span></div>
                <div class="popup-row"><span class="popup-label">Revenue:</span><span class="popup-val" style="color:#00f2fe;">BDT ${{Number(o.total_revenue).toLocaleString()}}</span></div>
                <div class="popup-row"><span class="popup-label">Orders:</span><span class="popup-val">${{o.total_orders}} Orders</span></div>
                <div class="popup-row"><span class="popup-label">SR Visits:</span><span class="popup-val">${{o.total_visits}} Visits</span></div>
                <div class="popup-row"><span class="popup-label">Tier:</span><span class="popup-val">${{o.tier}}</span></div>
                <div class="popup-row"><span class="popup-label">Status:</span><span class="popup-val" style="color:${{color}};">${{o.status_type}}</span></div>
            `;
            marker.bindPopup(popupContent, {{ className: 'custom-popup' }});

            if (o.status_type.includes("Blind Spot")) {{
                blindSpotsGroup.addLayer(marker);
            }} else if (o.status_type.includes("Red Flag")) {{
                redFlagsGroup.addLayer(marker);
            }} else {{
                clusterGroup.addLayer(marker);
            }}
        }});

        // 2. Heatmap Layer
        const heat = L.heatLayer(heatPoints, {{
            radius: 20,
            blur: 15,
            maxZoom: 14,
            gradient: {{ 0.2: '#00f2fe', 0.5: '#10b981', 0.8: '#f59e0b', 1.0: '#ef4444' }}
        }});
        heatLayerGroup.addLayer(heat);

        // 3. Top 300 Micro-Hubs Layer
        MAP_DATA.micro_hubs.forEach((hub, idx) => {{
            const hubCircle = L.circleMarker([hub.lat_grid, hub.long_grid], {{
                radius: Math.min(25, Math.max(8, Math.sqrt(hub.outlet_count) * 2.5)),
                fillColor: '#ef4444',
                color: '#fff',
                weight: 1.5,
                fillOpacity: 0.65
            }});
            const hubPopup = `
                <div class="popup-header">🔥 Top Micro-Hub #${{idx + 1}}</div>
                <div class="popup-row"><span class="popup-label">Outlets in Hub:</span><span class="popup-val">${{hub.outlet_count}} Stores</span></div>
                <div class="popup-row"><span class="popup-label">Hub Revenue:</span><span class="popup-val" style="color:#00f2fe;">BDT ${{Number(hub.hub_revenue).toLocaleString()}}</span></div>
                <div class="popup-row"><span class="popup-label">Total Visits:</span><span class="popup-val">${{hub.hub_visits}} Visits</span></div>
            `;
            hubCircle.bindPopup(hubPopup, {{ className: 'custom-popup' }});
            microHubsGroup.addLayer(hubCircle);
        }});

        // 4. SR Journey Routes
        MAP_DATA.sr_routes.forEach(route => {{
            const latlngs = route.points.map(p => [p.lat, p.lng]);
            const polyline = L.polyline(latlngs, {{
                color: '#38bdf8',
                weight: 3,
                opacity: 0.8,
                dashArray: '4, 8'
            }});
            polyline.bindPopup(`<div class="popup-header">SR Movement Tracking: ${{route.sr_id}}</div><div class="popup-row"><span class="popup-label">GPS Waypoints:</span><span class="popup-val">${{route.points.length}}</span></div>`, {{ className: 'custom-popup' }});
            routesGroup.addLayer(polyline);
        }});

        // Default Active Layers
        map.addLayer(clusterGroup);

        // Toggle Layer Handlers
        const activeState = {{
            tiers: true,
            heatmap: false,
            microhubs: false,
            blindspots: false,
            redflags: false,
            routes: false
        }};

        function toggleLayer(layerKey) {{
            activeState[layerKey] = !activeState[layerKey];
            const btn = document.getElementById('btn-' + layerKey);
            if (activeState[layerKey]) {{
                btn.classList.add('active');
            }} else {{
                btn.classList.remove('active');
            }}

            if (layerKey === 'tiers') {{
                if (activeState.tiers) map.addLayer(clusterGroup); else map.removeLayer(clusterGroup);
            }} else if (layerKey === 'heatmap') {{
                if (activeState.heatmap) map.addLayer(heatLayerGroup); else map.removeLayer(heatLayerGroup);
            }} else if (layerKey === 'microhubs') {{
                if (activeState.microhubs) map.addLayer(microHubsGroup); else map.removeLayer(microHubsGroup);
            }} else if (layerKey === 'blindspots') {{
                if (activeState.blindspots) map.addLayer(blindSpotsGroup); else map.removeLayer(blindSpotsGroup);
            }} else if (layerKey === 'redflags') {{
                if (activeState.redflags) map.addLayer(redFlagsGroup); else map.removeLayer(redFlagsGroup);
            }} else if (layerKey === 'routes') {{
                if (activeState.routes) map.addLayer(routesGroup); else map.removeLayer(routesGroup);
            }}
        }}

        function zoomTo(lat, lng, zoomLevel) {{
            map.flyTo([lat, lng], zoomLevel, {{ duration: 1.5 }});
        }}
    </script>
</body>
</html>
"""

with open(r"E:\ITL FINAL ADV ANALYSIS\geo_intelligence_explorer.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("Interactive Web Map 'geo_intelligence_explorer.html' created successfully!")
