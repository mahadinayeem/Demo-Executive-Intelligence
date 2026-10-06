"""
Upgrade ceo_national_map.html with Dynamic Scope Masking:
- National: Only Bangladesh is visible
- Division Click (e.g. Dhaka): ONLY Dhaka Division is visible, everything else masked white
- District Click (e.g. Gazipur): ONLY Gazipur District is visible, everything else masked white
- Thana Click (e.g. Sreepur): ONLY Sreepur Thana is visible with individual dots, everything else masked white
"""

path = r'd:\ITL FINAL ADV ANALYSIS\ceo_national_map.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace renderInverseMask with updateDynamicInverseMask
old_mask_fn = '''/* ═══════════════ BANGLADESH INVERSE COUNTRY MASK (HIDES FOREIGN TERRITORY) ═══════════════ */
function renderInverseMask() {
  if (!maskLayer || !map) return;
  maskLayer.clearLayers();
  if (typeof BD_INVERSE_MASK !== 'undefined') {
    const maskPoly = L.geoJSON(BD_INVERSE_MASK, {
      interactive: false,
      pane: 'maskPane',
      style: () => ({
        fillColor: isDark ? '#0b0f19' : '#ffffff',
        fillOpacity: 1.0,
        color: isDark ? '#1e293b' : '#e2e8f0',
        weight: 1.5,
        opacity: 1.0
      })
    });
    maskLayer.addLayer(maskPoly);
  }
}'''

new_mask_fn = '''/* ═══════════════ DYNAMIC SCOPE INVERSE MASK (ISOLATES ACTIVE SELECTION) ═══════════════ */
function getFeatureRings(feat) {
  const rings = [];
  if (!feat || !feat.geometry) return rings;
  const geom = feat.geometry;
  if (geom.type === 'Polygon') {
    if (geom.coordinates && geom.coordinates[0]) rings.push(geom.coordinates[0]);
  } else if (geom.type === 'MultiPolygon') {
    if (geom.coordinates) {
      geom.coordinates.forEach(poly => {
        if (poly && poly[0]) rings.push(poly[0]);
      });
    }
  }
  return rings;
}

function renderInverseMask() {
  if (!maskLayer || !map) return;
  maskLayer.clearLayers();

  const worldRing = [
    [-180.0, 90.0],
    [-180.0, -90.0],
    [180.0, -90.0],
    [180.0, 90.0],
    [-180.0, 90.0]
  ];

  let targetFeature = null;

  if (activeThana && typeof BD_THANAS_GEO !== 'undefined' && BD_THANAS_GEO.features) {
    targetFeature = BD_THANAS_GEO.features.find(f => 
      f.properties.thana && f.properties.thana.toLowerCase() === activeThana.toLowerCase() &&
      (!activeDistrict || (f.properties.district && f.properties.district.toLowerCase() === activeDistrict.toLowerCase()))
    );
  } else if (activeDistrict && typeof BD_DISTRICTS_GEO !== 'undefined' && BD_DISTRICTS_GEO.features) {
    targetFeature = BD_DISTRICTS_GEO.features.find(f => 
      f.properties.district && f.properties.district.toLowerCase() === activeDistrict.toLowerCase()
    );
  } else if (activeDivision && typeof BD_DIVISIONS_GEO !== 'undefined' && BD_DIVISIONS_GEO.features) {
    targetFeature = BD_DIVISIONS_GEO.features.find(f => 
      f.properties.name && f.properties.name.toLowerCase() === activeDivision.toLowerCase()
    );
  }

  let maskCoords = [worldRing];

  if (targetFeature) {
    const rings = getFeatureRings(targetFeature);
    rings.sort((a,b) => b.length - a.length);
    if (rings.length > 0) {
      maskCoords = [worldRing, ...rings];
    }
  } else if (typeof BD_INVERSE_MASK !== 'undefined') {
    maskCoords = BD_INVERSE_MASK.geometry.coordinates;
  }

  const maskGeoJSON = {
    type: "Feature",
    properties: { name: "Dynamic_Scope_Mask" },
    geometry: {
      type: "Polygon",
      coordinates: maskCoords
    }
  };

  const maskPoly = L.geoJSON(maskGeoJSON, {
    interactive: false,
    pane: 'maskPane',
    style: () => ({
      fillColor: isDark ? '#0b0f19' : '#ffffff',
      fillOpacity: 1.0,
      color: isDark ? '#1e293b' : '#cbd5e1',
      weight: 1.5,
      opacity: 1.0
    })
  });

  maskLayer.addLayer(maskPoly);
}'''

content = content.replace(old_mask_fn, new_mask_fn)

# Ensure renderInverseMask() is called on every drill step
# In drillDivision
content = content.replace("drawDistrictPolygons(sDiv, sIdx);", "drawDistrictPolygons(sDiv, sIdx);\n  renderInverseMask();")
content = content.replace("drawDistrictPolygons(divName, divIdx);", "drawDistrictPolygons(divName, divIdx);\n  renderInverseMask();")

# In drillDistrict
content = content.replace("drawThanaPolygons(distName, divIdx);", "drawThanaPolygons(distName, divIdx);\n  renderInverseMask();")

# In drillThana
content = content.replace("setTimeout(() => renderMicroOutlets(divIdx, distName, thanaName), 200);",
                          "renderInverseMask();\n  setTimeout(() => renderMicroOutlets(divIdx, distName, thanaName), 200);")

# In resetNational
content = content.replace("drawDivisionPolygons();", "drawDivisionPolygons();\n  renderInverseMask();")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied Dynamic Scope Mask successfully!")
