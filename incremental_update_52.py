import pandas as pd
import os
import time

# Configuration
RESULTS_CSV = 'retry_failed_52_results.csv'
TARGET_EXCEL = 'final_output/Instagram_Final_Merged.xlsx'

def update_excel():
    print("\n" + "="*60)
    print("INCREMENTAL UPDATE (52 RETRY)")
    print("="*60)

    if not os.path.exists(RESULTS_CSV):
        print(f"Waiting for results... ({RESULTS_CSV} not found yet)")
        return

    try:
        print(f"Reading {RESULTS_CSV}...")
        new_results_df = pd.read_csv(RESULTS_CSV)
        if new_results_df.empty:
            print("Results file is empty.")
            return
        
        success_df = new_results_df[new_results_df['status'] == 'Success']
        print(f"Found {len(new_results_df)} total rows, {len(success_df)} successful updates.")

        print(f"Reading target Excel: {TARGET_EXCEL}...")
        xls = pd.ExcelFile(TARGET_EXCEL)
        posts_df = pd.read_excel(xls, 'Posts_Reels')
        profiles_df = pd.read_excel(xls, 'Profiles')

        update_map = dict(zip(success_df['url'], success_df['views']))
        
        updated_count = 0
        for url, views in update_map.items():
            mask = posts_df['url'] == url
            if mask.any():
                posts_df.loc[mask, 'views'] = views
                posts_df.loc[mask, 'status'] = 'Success'
                updated_count += 1
        
        print(f"Updated {updated_count} rows in dataframe.")

        print(f"Saving to {TARGET_EXCEL}...")
        with pd.ExcelWriter(TARGET_EXCEL, engine='openpyxl') as writer:
            posts_df.to_excel(writer, sheet_name='Posts_Reels', index=False)
            profiles_df.to_excel(writer, sheet_name='Profiles', index=False)
            
        print(f"✅ Successfully updated {TARGET_EXCEL}")

    except Exception as e:
        print(f"❌ Error during update: {e}")

if __name__ == "__main__":
    update_excel()
