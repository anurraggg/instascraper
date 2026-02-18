import pandas as pd
import os
import glob

# Load Output
output_file = 'output/instagram_data_new.xlsx'
if not os.path.exists(output_file):
    print("Output file not found!")
    exit()

df = pd.read_excel(output_file)
# Assumes the order in df matches the input URLs/file naming 1..N
# df index 0 -> url_1

deleted_count = 0

for index, row in df.iterrows():
    if row['status'] != 'Success':
        file_num = index + 1
        
        # Files to delete
        log_file = f"logs_new/url_{file_num}.txt"
        json_file = f"logs_new/url_{file_num}_result.json"
        
        if os.path.exists(log_file):
            print(f"Deleting failed log: {log_file}")
            os.remove(log_file)
            deleted_count += 1
            
        if os.path.exists(json_file):
            os.remove(json_file)

print(f"\nDeleted {deleted_count} failed logs. Rerunning scraper will process these {deleted_count} URLs.")
