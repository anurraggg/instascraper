"""
Analyze Inputs vs Compiled Output
"""
import pandas as pd
from pathlib import Path

print("="*60)
print("ANALYSIS")
print("="*60)

# 1. Load Inputs
input_urls = set()

# CSV
try:
    df_csv = pd.read_csv('input/Instagram_URLS.csv')
    urls_csv = df_csv.iloc[:, 0].dropna().astype(str).str.strip().tolist()
    input_urls.update(urls_csv)
    print(f"✓ Loaded CSV: {len(urls_csv)} URLs")
except Exception as e:
    print(f"✗ Error loading CSV: {e}")

# Excel
try:
    df_xlsx = pd.read_excel('input/INSTAURL.xlsx')
    urls_xlsx = df_xlsx.iloc[:, 0].dropna().astype(str).str.strip().tolist()
    input_urls.update(urls_xlsx)
    print(f"✓ Loaded XLSX: {len(urls_xlsx)} URLs")
except Exception as e:
    print(f"✗ Error loading XLSX: {e}")

print(f"Total Unique Input URLs: {len(input_urls)}")

# 2. Load Compiled Output
try:
    compiled_file = 'final_output/Instagram_Data_Compiled.xlsx'
    df_posts = pd.read_excel(compiled_file, sheet_name='Posts_Reels')
    df_profiles = pd.read_excel(compiled_file, sheet_name='Profiles')
    
    print(f"\nCompiled Data:")
    print(f"  Posts: {len(df_posts)}")
    print(f"  Profiles: {len(df_profiles)}")
    
    # Check for 0 views in Posts
    zero_views = df_posts[df_posts['views'] == 0]
    print(f"\n⚠ Posts with 0 Views: {len(zero_views)}")
    
    if len(zero_views) > 0:
        print("Saving 0-view URLs to 're_retry_list.csv'...")
        zero_views[['url']].to_csv('re_retry_list.csv', index=False)
        
except Exception as e:
    print(f"✗ Error loading compiled file: {e}")
