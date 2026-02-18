import pandas as pd

try:
    df = pd.read_excel("output/instagram_media.xlsx")
    print(f"Total rows: {len(df)}")
    
    success = df[df['status'] == 'Success']
    failed = df[df['status'] != 'Success']
    
    print(f"Success: {len(success)}")
    print(f"Failed: {len(failed)}")
    
    if len(failed) > 0:
        print("\nFailed URLs:")
        print(failed[['url', 'error']].head(10))
        
    print("\nSample Success:")
    print(success[['shortcode', 'media_url', 'snapshot_path']].head())

except Exception as e:
    print(f"Error: {e}")
