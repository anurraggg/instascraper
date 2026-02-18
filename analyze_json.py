import re

def analyze_json():
    try:
        with open('debug_views.html', 'r', encoding='utf-8') as f:
            html = f.read()
        
        print("--- Searching for JSON Counts ---")
        
        # Video View Count
        matches = re.findall(r'"video_view_count":\s*(\d+)', html)
        print(f"Video View Count Matches: {matches}")
        
        # Play Count
        matches2 = re.findall(r'"play_count":\s*(\d+)', html)
        print(f"Play Count Matches: {matches2}")
        
        # Like Count (for verification)
        matches3 = re.findall(r'"edge_liked_by":\s*\{\s*"count":\s*(\d+)', html)
        print(f"Like Count Matches: {matches3}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_json()
