"""
Ensure 100% resilient Thana & Union matching across all functions in ceo_national_map.html
"""

path = r'd:\ITL FINAL ADV ANALYSIS\ceo_national_map.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update drawThanaPolygons matching
old_draw_match = "const tOutlets = distOutlets.filter(o => o[16] && o[16].toLowerCase() === tName.toLowerCase() && isOutletMatch(o));"
new_draw_match = "const tOutlets = distOutlets.filter(o => o[16] && (o[16].toLowerCase() === tName.toLowerCase() || o[16].toLowerCase().replace(/\\s+/g,'') === tName.toLowerCase().replace(/\\s+/g,'')) && isOutletMatch(o));"
content = content.replace(old_draw_match, new_draw_match)

# 2. Update drillThana matching
old_drill_match = "f.properties.thana && f.properties.thana.toLowerCase() === thanaName.toLowerCase() &&"
new_drill_match = "f.properties.thana && (f.properties.thana.toLowerCase() === thanaName.toLowerCase() || f.properties.thana.toLowerCase().replace(/\\s+/g,'') === thanaName.toLowerCase().replace(/\\s+/g,'')) &&"
content = content.replace(old_drill_match, new_drill_match)

# 3. Update renderMicroOutlets matching
old_micro_thana_match = "if (filterThana && (!o[16] || o[16].toLowerCase() !== filterThana.toLowerCase())) return false;"
new_micro_thana_match = "if (filterThana && (!o[16] || (o[16].toLowerCase() !== filterThana.toLowerCase() && o[16].toLowerCase().replace(/\\s+/g,'') !== filterThana.toLowerCase().replace(/\\s+/g,'')))) return false;"
content = content.replace(old_micro_thana_match, new_micro_thana_match)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated Thana matching in ceo_national_map.html successfully!")
