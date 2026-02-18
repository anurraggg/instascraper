import re
import json

def analyze_deep():
    try:
        with open('debug_views.html', 'r', encoding='utf-8') as f:
            html = f.read()
        
        print("--- Deep Analysis ---")
        
        # Find all JSON-like structures
        # This is a heuristic: look for {"key": ...} patterns or just large blocks of text starting with { and ending with }
        # But better: look for the known numbers.
        
        known_likes = "224"
        known_comments = "5"
        
        # Find context around known likes
        print(f"Searching for context around '{known_likes}'...")
        indices = [m.start() for m in re.finditer(known_likes, html)]
        for i in indices:
            start = max(0, i - 100)
            end = min(len(html), i + 100)
            context = html[start:end]
            print(f"Match at {i}: ...{context}...")
            print("-" * 20)
            
        # Look for "video_view_count" again with case insensitivity and loose spacing
        print("\nSearching for 'view_count' variants...")
        matches = re.findall(r'view_count["\']?\s*:\s*(\d+)', html, re.I)
        print(f"Matches: {matches}")

        matches = re.findall(r'play_count["\']?\s*:\s*(\d+)', html, re.I)
        print(f"Matches: {matches}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_deep()
