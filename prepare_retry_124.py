import pandas as pd
import os

# Load results
df = pd.read_excel('output/instagram_data_new.xlsx')

# Filter failed entries
failed = df[df['status'] != 'Success']
print(f"Found {len(failed)} failed URLs")

# Extract URLs
failed_urls = failed['url'].tolist()

# Save to input file
df_urls = pd.DataFrame(failed_urls)
df_urls.to_excel('input/INSTAURL.xlsx', index=False, header=False)
print(f"Saved {len(failed_urls)} URLs to input/INSTAURL.xlsx")

# Clear logs
log_dir = 'logs_new'
if os.path.exists(log_dir):
    for f in os.listdir(log_dir):
        os.remove(os.path.join(log_dir, f))
    print(f"Cleared {log_dir}")

# Remove temp outputs
if os.path.exists('output/instagram_data_final.xlsx'):
    os.remove('output/instagram_data_final.xlsx')

print("Ready for retry scrape.")
