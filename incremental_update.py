import pandas as pd
import time
import os

def update_excel():
    print("="*60)
    print("INCREMENTAL UPDATE")
    print("="*60)

    csv_file = 'final_retry_results.csv'
    compiled_file = 'final_output/Instagram_Data_Compiled.xlsx'
    final_file = 'final_output/Instagram_Final_Complete.xlsx'

    if not os.path.exists(csv_file):
        print(f"Waiting for {csv_file} to be created...")
        return

    try:
        # Read new results
        print(f"Reading {csv_file}...")
        new_data = pd.read_csv(csv_file)
        print(f"Found {len(new_data)} rows in CSV.")

        # Read existing compiled file
        print(f"Reading {compiled_file}...")
        df_posts = pd.read_excel(compiled_file, sheet_name='Posts_Reels')
        df_profiles = pd.read_excel(compiled_file, sheet_name='Profiles')

        # Update logic
        updated_count = 0
        for _, row in new_data.iterrows():
            url = row['url']
            views = row['views']
            status = row['status']
            
            # Only update if we have a valid view count or status change
            if views > 0 or status == 'Failed':
                mask = df_posts['url'] == url
                if mask.any():
                    df_posts.loc[mask, 'views'] = views
                    df_posts.loc[mask, 'status'] = status
                    updated_count += 1
        
        print(f"Updated {updated_count} rows in memory.")

        # Save back to compiled file
        print(f"Saving to {compiled_file}...")
        with pd.ExcelWriter(compiled_file, engine='openpyxl') as writer:
            df_posts.to_excel(writer, sheet_name='Posts_Reels', index=False)
            df_profiles.to_excel(writer, sheet_name='Profiles', index=False)
        print("✓ Saved compiled file.")

        # Create final complete file
        print(f"Creating {final_file}...")
        with pd.ExcelWriter(final_file, engine='openpyxl') as writer:
            df_posts.to_excel(writer, sheet_name='Posts_Reels', index=False)
            df_profiles.to_excel(writer, sheet_name='Profiles', index=False)
        print(f"✅ Successfully updated {final_file}")

    except PermissionError:
        print("✗ Error: Permission denied. Please close the Excel file if it is open.")
    except Exception as e:
        print(f"✗ Error during update: {e}")

if __name__ == "__main__":
    update_excel()
