import pandas as pd
from pathlib import Path

# Load URLs from text file
with open('input/transcribed_urls.txt', 'r') as f:
    urls = [line.strip() for line in f if line.strip()]

# Create DataFrame with the expected column name
df = pd.DataFrame({'INSTAGRAM URL': urls})

# Save to Excel
df.to_excel('input/INSTAURL.xlsx', index=False)
print(f"Created input/INSTAURL.xlsx with {len(urls)} URLs")
