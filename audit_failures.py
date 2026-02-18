import pandas as pd
import os

df = pd.read_excel('output/instagram_data_final.xlsx')
failed = df[df['status'] != 'Success']

print(f"Auditing {len(failed)} failures...")

counters = {
    "Page Unavailable": 0,
    "Restricted": 0, 
    "Login Wall / Content Hidden": 0,
    "Log Empty/Short": 0,
    "Content Loaded but Regex Failed": 0,
    "Unknown": 0
}

regex_failed_urls = []

for i, row in failed.iterrows():
    idx = i + 1
    log_file = f"logs_new/url_{idx}.txt"
    
    reason = "Unknown"
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "Sorry, this page isn't available." in content:
            reason = "Page Unavailable"
        elif "Restricted profile" in content:
            reason = "Restricted"
        elif "Log in to Instagram" in content and "See all posts" not in content:
            reason = "Login Wall / Content Hidden"
        else:
            # Check if empty or short
            if len(content) < 500:
                reason = "Log Empty/Short"
            elif "0 likes" not in content and "No post data found" not in content: # means content is there?
                 reason = "Content Loaded but Regex Failed"
                 regex_failed_urls.append(idx)
            else:
                 reason = "Content Loaded but Regex Failed" # Fallback
                 regex_failed_urls.append(idx)

    counters[reason] += 1

print("\nFailure Summary:")
for k, v in counters.items():
    print(f"{k}: {v}")

print(f"\nRegex Failed URLs: {regex_failed_urls}")
