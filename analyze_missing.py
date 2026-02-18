import pandas as pd

def analyze_missing():
    output_file = 'output/instagram_auto.xlsx'
    
    try:
        df = pd.read_excel(output_file)
        # Filter for missing usernames (NaN or empty string)
        missing_df = df[df['username'].isna() | (df['username'] == '')]
        
        print(f"Found {len(missing_df)} rows with missing usernames.")
        
        if not missing_df.empty:
            print("\nURLs with missing usernames:")
            print("\nURLs with missing usernames:")
            for index, row in missing_df.iterrows():
                print(f"Row {index + 2}: {row['url']} | Status: {row.get('status', 'N/A')} | Error: {row.get('error', 'N/A')}")
                
            # Save to a temporary file for easy access if needed
            missing_df.to_excel('output/missing_usernames.xlsx', index=False)
            print("\nSaved missing entries to 'output/missing_usernames.xlsx'")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_missing()
