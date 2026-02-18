import json
from bs4 import BeautifulSoup
import re

def find_keys(node, kv):
    if isinstance(node, list):
        for i in node:
            find_keys(i, kv)
    elif isinstance(node, dict):
        for k, v in node.items():
            if 'view_count' in k or 'play_count' in k or 'video_view_count' in k:
                kv[k] = v
            find_keys(v, kv)

def main():
    with open("debug_views.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="application/json")
    
    print(f"Found {len(scripts)} JSON scripts.")
    
    found_data = {}
    
    for i, script in enumerate(scripts):
        try:
            data = json.loads(script.string)
            find_keys(data, found_data)
        except:
            pass
            
    # Also check for variable assignment in other scripts
    # window.__additionalDataLoaded('...', data)
    scripts_js = soup.find_all("script")
    for script in scripts_js:
        if script.string and "video_view_count" in script.string:
            print("Found video_view_count in JS script content!")
            # Try to extract it with regex
            m = re.findall(r'"video_view_count":(\d+)', script.string)
            if m:
                found_data["video_view_count_regex"] = m
                
    print("\n--- Found Data ---")
    for k, v in found_data.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
