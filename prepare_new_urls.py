import pandas as pd

# Read URLs from text file
with open('input/new_batch_urls.txt', 'r') as f:
    urls = [line.strip() for line in f if line.strip()]

print(f"Found {len(urls)} URLs")

# Save to Excel input file (no header)
df = pd.DataFrame(urls)
df.to_excel('input/INSTAURL.xlsx', index=False, header=False)
print(f"Saved to input/INSTAURL.xlsx")

# Clear logs
import os
log_dir = 'logs_new'
if os.path.exists(log_dir):
    for f in os.listdir(log_dir):
        os.remove(os.path.join(log_dir, f))
    print(f"Cleared {log_dir}")

print("Ready to scrape new batch.")
