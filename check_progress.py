import pandas as pd
import os

def check_file(path, name):
    if not os.path.exists(path):
        print(f"[-] {name}: File not found at {path}")
        return 0
    
    try:
        # Try reading with openpyxl engine explicitly
        df = pd.read_excel(path, engine='openpyxl')
        print(f"[+] {name}: Found {len(df)} rows.")
        return len(df)
    except Exception as e:
        print(f"[-] {name}: Error reading file: {e}")
        # Try reading file size
        try:
            size = os.path.getsize(path)
            print(f"    File size: {size} bytes")
        except:
            pass
        return 0

print("--- Status Report ---")
input_count = check_file('input/INSTAURL.xlsx', 'Input URLs')
output_count = check_file('output/instagram_fresh_results.xlsx', 'Output Results')

if input_count > 0:
    progress = (output_count / input_count) * 100
    print(f"Progress: {progress:.1f}% ({output_count}/{input_count})")
else:
    print("Progress: 0% (No input data found)")
