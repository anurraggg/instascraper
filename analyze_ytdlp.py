import json
import os

def analyze_ytdlp():
    print("Analyzing debug_ytdlp.json...")
    
    if not os.path.exists("debug_ytdlp.json"):
        print("❌ File not found.")
        return

    content = ""
    try:
        with open("debug_ytdlp_mobile.json", "r", encoding="utf-16") as f:
            content = f.read()
    except:
        try:
            with open("debug_ytdlp_mobile.json", "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return

    if not content.strip():
        print("❌ File is empty.")
        return

    try:
        data = json.loads(content)
        print(f"✅ JSON Parsed Successfully!")
        
        # Recursive search
        def find_keys(node, path=""):
            if isinstance(node, dict):
                for k, v in node.items():
                    new_path = f"{path}.{k}" if path else k
                    if "view" in k.lower() or "play" in k.lower():
                        print(f"  🎯 Found Key: {new_path} = {v}")
                    
                    if isinstance(v, (dict, list)):
                        find_keys(v, new_path)
            elif isinstance(node, list):
                for i, item in enumerate(node):
                    find_keys(item, f"{path}[{i}]")

        find_keys(data)
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        print("First 500 chars of content:")
        print(content[:500])

if __name__ == "__main__":
    analyze_ytdlp()
