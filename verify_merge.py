import pandas as pd
import shutil
import os

def verify_and_merge():
    retry_file = 'output/retry_results.xlsx'
    main_file = 'output/instagram_auto.xlsx'
    
    if not os.path.exists(retry_file):
        print(f"Retry file '{retry_file}' not found.")
        return

    try:
        df_retry = pd.read_excel(retry_file)
        print(f"Retry file has {len(df_retry)} rows.")
        
        # Check success rate
        success_count = df_retry[df_retry['username'].notna() & (df_retry['username'] != '')].shape[0]
        print(f"Successfully extracted usernames: {success_count}/{len(df_retry)}")
        
        if success_count < len(df_retry):
            print("Warning: Some usernames are still missing.")
            print(df_retry[df_retry['username'].isna() | (df_retry['username'] == '')]['url'].tolist())
        
        # Merge
        if os.path.exists(main_file):
            print(f"\nMerging into '{main_file}'...")
            df_main = pd.read_excel(main_file)
            
            # Create a dictionary from retry results for easy lookup
            retry_dict = df_retry.set_index('url').to_dict('index')
            
            updated_count = 0
            for index, row in df_main.iterrows():
                url = row['url']
                if url in retry_dict:
                    # Update row with new data
                    for col, val in retry_dict[url].items():
                        df_main.at[index, col] = val
                    updated_count += 1
            
            print(f"Updated {updated_count} rows in main file.")
            
            # Backup original
            shutil.copy(main_file, main_file + '.bak')
            print(f"Backed up original to '{main_file}.bak'")
            
            # Save merged
            df_main.to_excel(main_file, index=False)
            print(f"Saved merged file to '{main_file}'")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_and_merge()
