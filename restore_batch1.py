import pandas as pd
import os
import shutil

# Correct source based on previous check
source_file = 'output/instagram_results_final.xlsx'

if not os.path.exists(source_file):
    print(f"Error: {source_file} not found.")
    exit(1)

print(f"Reading URLs from {source_file}...")
df = pd.read_excel(source_file)

if 'URL' not in df.columns:
    print("Error: 'URL' column not found in source file.")
    print(f"Columns found: {df.columns.tolist()}")
    exit(1)

urls = df['URL'].dropna().tolist()
print(f"Found {len(urls)} URLs.")

# Write to input file (no header)
df_urls = pd.DataFrame(urls)
df_urls.to_excel('input/INSTAURL.xlsx', index=False, header=False)
print(f"Restored {len(urls)} URLs to input/INSTAURL.xlsx")

# Clear logs
log_dir = 'logs_new'
if os.path.exists(log_dir):
    for f in os.listdir(log_dir):
        os.remove(os.path.join(log_dir, f))
    print(f"Cleared {log_dir}")

# Remove previous outputs to avoid confusion
if os.path.exists('output/instagram_data_final.xlsx'):
    os.remove('output/instagram_data_final.xlsx')
if os.path.exists('output/instagram_data_new.xlsx'):
    os.remove('output/instagram_data_new.xlsx')

print("Ready for re-scrape of Batch 1.")
