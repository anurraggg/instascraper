import json
import pandas as pd
from pathlib import Path
import glob
import os

def generate_excel():
    print("Compiling logs into Excel...")
    results = []
    
    # Target Directory
    log_dir = "logs_backup_20251218_104123"
    if not os.path.exists(log_dir):
        print(f"❌ Directory {log_dir} not found.")
        return

    # Find all JSON log files
    # Pattern: url_X_data.json or just *.json
    log_files = glob.glob(f"{log_dir}/*.json")
    print(f"Found {len(log_files)} log files in {log_dir}.")
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure all fields exist (handle older logs)
                if 'followers' not in data: data['followers'] = 0
                if 'following' not in data: data['following'] = 0
                results.append(data)
        except Exception as e:
            # print(f"Error reading {log_file}: {e}")
            pass
            
    if not results:
        print("No results found.")
        return

    print(f"Successfully loaded {len(results)} JSON objects.")

    # Create DataFrame
    final_df = pd.DataFrame(results)
    
    # Reorder columns
    cols = ['url', 'likes', 'comments', 'views', 'followers', 'following', 'collaborators', 'status', 'error']
    # Add missing cols if any
    for col in cols:
        if col not in final_df.columns:
            final_df[col] = ''
            
    final_df = final_df[cols]
    
    # Filter for Success
    success_df = final_df[final_df['status'] == 'Success']
    print(f"Successful Rows: {len(success_df)}")
    print(f"Total Views Captured: {success_df['views'].sum()}")
    
    output_file = 'output/instagram_recovered_backup.xlsx'
    final_df.to_excel(output_file, index=False)
    print(f"✅ Saved recovered data to: {output_file}")
    print(f"Total Rows: {len(final_df)}")

if __name__ == "__main__":
    generate_excel()
