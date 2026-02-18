import pandas as pd

try:
    file_path = 'output/instagram_recovered_backup.xlsx'
    df = pd.read_excel(file_path)
    
    print(f"Total Rows: {len(df)}")
    print(f"Success Rows: {len(df[df['status'] == 'Success'])}")
    
    # Check for non-zero views
    views_df = df[df['views'] > 0]
    print(f"Rows with Views > 0: {len(views_df)}")
    
    print("\nSample Data (First 5 with views):")
    print(views_df[['url', 'views', 'likes', 'comments']].head(5).to_string())
    
    # Check if target URL is in there
    target = "https://www.instagram.com/reel/DM5F3Vzq6TN/"
    target_row = df[df['url'].astype(str).str.contains("DM5F3Vzq6TN")]
    if not target_row.empty:
        print("\nTarget URL Found:")
        print(target_row[['url', 'views', 'status']].to_string())
    else:
        print("\nTarget URL NOT Found in recovered data.")

except Exception as e:
    print(f"Error: {e}")
