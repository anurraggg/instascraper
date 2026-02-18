import json
import glob
import os

def check_logs_new():
    print("Checking logs_new...")
    files = glob.glob("logs_new/*.json")
    print(f"Found {len(files)} files.")
    
    count_views = 0
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if data.get('views', 0) > 0:
                    count_views += 1
        except: pass
        
    print(f"Files with views > 0: {count_views}")

if __name__ == "__main__":
    check_logs_new()
