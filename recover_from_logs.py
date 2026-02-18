import os
import re
import json
import pandas as pd
from datetime import datetime

def extract_number(text):
    if not text: return 0
    text = str(text).strip().upper().replace(',', '')
    multiplier = 1
    if 'K' in text:
        multiplier = 1000
        text = text.replace('K', '')
    elif 'M' in text:
        multiplier = 1000000
        text = text.replace('M', '')
    try:
        match = re.search(r'[\d.]+', text)
        if match:
            return int(float(match.group()) * multiplier)
    except:
        pass
    return 0

log_dir = 'logs_new'
output_file = 'output/instagram_data_final.xlsx'

# Load original output to preserve order/urls
try:
    df_orig = pd.read_excel('output/instagram_data_new.xlsx')
    results = df_orig.to_dict('records')
except:
    print("Original output not found, starting fresh mapping not possible easily without input file.")
    # Fallback to input file logic if needed, but let's assume it exists.
    exit()

print(f"Loaded {len(results)} records.")

updates = 0

for i, row in enumerate(results):
    url = row['url']
    # Match log file index (1-based)
    # df index 0 -> url_1
    idx = i + 1
    log_file = f"{log_dir}/url_{idx}.txt"
    
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        likes = row['likes']
        comments = row['comments']
        status = row['status']
        
        # Only try to improve if Failed or No Data (or 0 likes)
        if status != 'Success' or likes == 0:
            lines = content.split('\n')
            
            new_likes = 0
            new_comments = 0
            
            # Strategy 1: Look for number before Date
            # Date usually has "January", "February", etc. or "hours ago", "days ago"
            # And year like "2024", "2025"
            for j, line in enumerate(lines):
                line = line.strip()
                
                # Identify Date line
                is_date = False
                if re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}', line):
                    is_date = True
                elif re.search(r'\d+\s+(hours|days|minutes|seconds)\s+ago', line):
                    is_date = True
                elif re.match(r'^[A-Za-z]+\s+\d{1,2}$', line): # e.g. "October 5" (current year implied)
                     is_date = True
                     
                if is_date and j > 0:
                    # Check previous line for number
                    prev_line = lines[j-1].strip()
                    if re.match(r'^[\d,\.]+[KMB]?$', prev_line):
                        # Potential Likes
                        val = extract_number(prev_line)
                        if val > 0:
                            new_likes = val
                            print(f"[Fixed] URL {idx}: found {new_likes} likes (Date context)")
                            break
            
            # Strategy 2: "View all X comments"
            if new_comments == 0:
                 comm_match = re.search(r'View all (\d+) comments', content)
                 if comm_match:
                     new_comments = extract_number(comm_match.group(1))
                     
            if new_likes > 0:
                row['likes'] = new_likes
                row['status'] = 'Success' # Assume success if we found likes
                updates += 1
                
            if new_comments > 0:
                row['comments'] = new_comments
                if row['status'] != 'Success':
                     row['status'] = 'Success'
                # Don't increment updates if only comments found? 
                # actually yes, it's an improvement.
                
            results[i] = row

df_final = pd.DataFrame(results)
df_final.to_excel(output_file, index=False)
print(f"Saved refined data to {output_file}. Total updates: {updates}")
