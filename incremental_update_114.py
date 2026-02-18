import pandas as pd
import os
import time
from pathlib import Path

# Configuration
RESULTS_CSV = 'retry_failed_114_results.csv'
BASE_EXCEL = 'final_output/Instagram_Final_Complete.xlsx'
OUTPUT_EXCEL = 'final_output/Instagram_Final_Updated_114.xlsx'

def update_excel():
    print("\n" + "="*60)
    print("INCREMENTAL UPDATE (114 RETRY)")
    print("="*60)

    # 1. Check if results CSV exists
    if not os.path.exists(RESULTS_CSV):
        print(f"Waiting for results... ({RESULTS_CSV} not found yet)")
        return

    try:
        # 2. Read new results
        print(f"Reading {RESULTS_CSV}...")
        new_results_df = pd.read_csv(RESULTS_CSV)
        if new_results_df.empty:
            print("Results file is empty.")
            return
        
        # Filter for successes only to update
        success_df = new_results_df[new_results_df['status'] == 'Success']
        print(f"Found {len(new_results_df)} total rows, {len(success_df)} successful updates.")

        # 3. Read Base Excel
        print(f"Reading base Excel: {BASE_EXCEL}...")
        # We need to read both sheets to preserve them, but we only update Posts_Reels usually
        xls = pd.ExcelFile(BASE_EXCEL)
        posts_df = pd.read_excel(xls, 'Posts_Reels')
        profiles_df = pd.read_excel(xls, 'Profiles')

        # 4. Update Data
        # Create a mapping of URL -> Views from the new results
        update_map = dict(zip(success_df['url'], success_df['views']))
        
        updated_count = 0
        for url, views in update_map.items():
            # Find row in posts_df
            mask = posts_df['url'] == url
            if mask.any():
                posts_df.loc[mask, 'views'] = views
                posts_df.loc[mask, 'status'] = 'Success'
                updated_count += 1
        
        print(f"Updated {updated_count} rows in dataframe.")

        # 5. Save to NEW Excel file
        print(f"Saving to {OUTPUT_EXCEL}...")
        with pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl') as writer:
            posts_df.to_excel(writer, sheet_name='Posts_Reels', index=False)
            profiles_df.to_excel(writer, sheet_name='Profiles', index=False)
            
        print(f"✅ Successfully created/updated {OUTPUT_EXCEL}")

    except Exception as e:
        print(f"❌ Error during update: {e}")

if __name__ == "__main__":
    update_excel()
