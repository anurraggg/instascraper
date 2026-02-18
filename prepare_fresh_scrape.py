import pandas as pd
import os

# Read the original 217 URLs
with open('input/new_urls_217.txt', 'r') as f:
    urls = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]

print(f"Found {len(urls)} Instagram URLs")

# Save to Excel input file (no header)
df = pd.DataFrame(urls)
df.to_excel('input/INSTAURL.xlsx', index=False, header=False)
print(f"Saved to input/INSTAURL.xlsx")

# Clear logs for fresh run
log_dir = 'logs_new'
if os.path.exists(log_dir):
    for f in os.listdir(log_dir):
        os.remove(os.path.join(log_dir, f))
    print(f"Cleared {log_dir}")

# Remove old outputs
if os.path.exists('output/instagram_data_new.xlsx'):
    os.remove('output/instagram_data_new.xlsx')
if os.path.exists('output/instagram_data_final.xlsx'):
    os.remove('output/instagram_data_final.xlsx')

print("Ready to scrape with FIXED scraper.")
