"""
Instagram Scraper - COMPILE RESULTS
Merges data from multiple runs, removes duplicates, and segregates by type.
"""

import pandas as pd
from pathlib import Path
import re

print("\n" + "="*60)
print("INSTAGRAM DATA COMPILER")
print("="*60)

# 1. Load Data
files_to_load = [
    'output/instagram_data_v2.xlsx',      # Batch 1 + Retries
    'output/instagram_data_new_v3.xlsx'   # Batch 2 + Retries
]

dfs = []
for file in files_to_load:
    try:
        if Path(file).exists():
            df = pd.read_excel(file)
            print(f"✓ Loaded {file}: {len(df)} rows")
            dfs.append(df)
        else:
            print(f"⚠ File not found: {file}")
    except Exception as e:
        print(f"✗ Error loading {file}: {e}")

if not dfs:
    print("No data loaded!")
    exit()

# 2. Concatenate
full_df = pd.concat(dfs, ignore_index=True)
print(f"\nTotal rows before cleaning: {len(full_df)}")

# 3. Clean Data
# Standardize URL
full_df['url'] = full_df['url'].astype(str).str.strip()

# Remove Duplicates (keep last occurrence as it's likely the most recent/retried one)
full_df.drop_duplicates(subset=['url'], keep='last', inplace=True)
print(f"Total rows after removing duplicates: {len(full_df)}")

# 4. Segregate
def is_post(url):
    return '/p/' in url or '/reel/' in url or '/tv/' in url

full_df['is_post'] = full_df['url'].apply(is_post)

posts_df = full_df[full_df['is_post'] == True].copy()
profiles_df = full_df[full_df['is_post'] == False].copy()

# Select Columns
post_cols = ['url', 'likes', 'comments', 'views', 'collaborators', 'status', 'error']
profile_cols = ['url', 'followers', 'following', 'status', 'error']

# Ensure columns exist
for col in post_cols:
    if col not in posts_df.columns:
        posts_df[col] = ''
        
for col in profile_cols:
    if col not in profiles_df.columns:
        profiles_df[col] = ''

posts_final = posts_df[post_cols]
profiles_final = profiles_df[profile_cols]

print(f"\nSegregated Data:")
print(f"  📹 Posts/Reels: {len(posts_final)}")
print(f"  👤 Profiles: {len(profiles_final)}")

# 5. Save
Path('final_output').mkdir(exist_ok=True)
output_file = 'final_output/Instagram_Data_Compiled.xlsx'

try:
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        posts_final.to_excel(writer, sheet_name='Posts_Reels', index=False)
        profiles_final.to_excel(writer, sheet_name='Profiles', index=False)
    print(f"\n✅ Saved compiled data to: {output_file}")
except Exception as e:
    print(f"\n✗ Error saving file: {e}")
    print("👉 Please close the Excel file if it is open!")

print("="*60)
