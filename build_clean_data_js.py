import json
import re

print("--- Checking HTML and JSON validity ---")

# 1. Load module1_full_suite_data.json
with open(r"E:\ITL FINAL ADV ANALYSIS\module1_full_suite_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Sanitize strings to avoid any JS breaks
def sanitize_obj(obj):
    if isinstance(obj, dict):
        return {k: sanitize_obj(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_obj(x) for x in obj]
    elif isinstance(obj, str):
        # clean problematic characters
        return obj.replace('"', ' ').replace("'", " ").replace('\n', ' ').replace('\r', ' ').replace('\\', ' ')
    return obj

clean_data = sanitize_obj(data)

# Save as separate data.js file so HTML stays clean, fast and without inline parsing errors!
with open(r"E:\ITL FINAL ADV ANALYSIS\map_suite_data.js", "w", encoding="utf-8") as f:
    f.write("const DATA = " + json.dumps(clean_data, ensure_ascii=False) + ";\n")

print("Saved map_suite_data.js successfully!")
