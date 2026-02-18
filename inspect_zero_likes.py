import pandas as pd
import os
import re

# Load results
df = pd.read_excel('output/instagram_data_final.xlsx')

# Filter for 0 likes
zero_likes = df[df['likes'] == 0]
print(f"Found {len(zero_likes)} entries with 0 likes")

results_to_update = []

for index, row in zero_likes.iterrows():
    url = row['url']
    print(f"\nChecking: {url}")
    
    # distinct 'url_{i}.txt' logic is tricky if we don't know 'i'. 
    # But the scraper saves logs based on index. 
    # I need to find the corresponding log file.
    # The scraper loop was: for i, url in enumerate(urls, 1):
    
    # I will reload the input list to map URL to index
    input_df = pd.read_excel('input/INSTAURL.xlsx')
    input_urls = input_df.iloc[:, 0].dropna().tolist()
    input_urls = [u.strip() for u in input_urls if isinstance(u, str) and u.strip().startswith('http')]
    
    # Normalize URL for comparison
    def normalize_url(u):
        if not isinstance(u, str): return ""
        u = u.strip()
        if "?" in u:
            u = u.split("?")[0]
        if u.endswith("/"):
            u = u[:-1]
        return u
        
    target_norm = normalize_url(url)
    
    # Check input URLs
    found_idx = -1
    for i, input_url in enumerate(input_urls, 1):
        if normalize_url(input_url) == target_norm:
            found_idx = i
            break
            
    if found_idx != -1:
        log_file = f"logs_new/url_{found_idx}.txt"
        
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Check for hidden indicators
            is_hidden = False
            
            # --- HIDDEN INDICATORS ---
            # 1. Explicit text
            if "like count hidden" in content.lower():
                is_hidden = True
            elif "likes are hidden" in content.lower():
                is_hidden = True
            
            # 2. "Liked by X and others" without a count
            # Use regex to find "Liked by ... and others"
            # If we see this, but our main scraper extracted 0, it likely means no count was visible
            elif "Liked by" in content and "others" in content:
                # Let's verify if there is actually NO number
                 if not re.search(r'and\s+[\d,]+\s+others', content):
                     is_hidden = True
            
            if is_hidden:
                print(f"  -> Detected as HIDDEN (Log: {log_file})")
                results_to_update.append((index, 'Hidden'))
            else:
                print(f"  -> No 'hidden' text found in {log_file}.")
                # Print a snippet for debugging
                snippet = content[:500].replace('\n', ' ')
                print(f"     Snippet: {snippet}...")
        else:
            print(f"  -> Log file {log_file} not found")
    else:
        print(f"  -> URL not found in input list: {url}")

# Update DataFrame
if results_to_update:
    print(f"\nUpdating {len(results_to_update)} rows...")
    # We need to change the column type to object to allow strings
    df['likes'] = df['likes'].astype(object)
    
    for idx, new_val in results_to_update:
        df.at[idx, 'likes'] = new_val
        
    df.to_excel('output/instagram_data_final_checked.xlsx', index=False)
    print("Saved to output/instagram_data_final_checked.xlsx")
else:
    print("No updates made.")
