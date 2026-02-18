import pandas as pd
import os
import glob

print("Combining all successful scrapes into batch4.xlsx...")

# We need to collect all successful entries from multiple runs
# The data is scattered across different scrape runs

all_successful = []

# Check if there are any saved intermediate files
files_to_check = [
    'output/instagram_data_new.xlsx',
    'output/instagram_data_final.xlsx'
]

# Also check for any backup files from previous runs
backup_pattern = 'output/instagram_data_*.xlsx'
backup_files = glob.glob(backup_pattern)

print(f"\nFound potential data files:")
for f in files_to_check + backup_files:
    if os.path.exists(f):
        print(f"  - {f}")

# Strategy: We'll need to manually track which runs had successes
# Based on the conversation:
# - First run: 75 successes (in some file)
# - Retry #1: 21 successes (in some file)  
# - Retry #2: 68 successes (likely in instagram_data_new.xlsx)
# - Retry #3: 0 successes

# Let's check what's in the current output file
if os.path.exists('output/instagram_data_new.xlsx'):
    df_current = pd.read_excel('output/instagram_data_new.xlsx')
    print(f"\nCurrent file has {len(df_current)} rows")
    print(f"  Success: {sum(df_current['status'] == 'Success')}")
    print(f"  Failed: {sum(df_current['status'] != 'Success')}")
    
    # This is from retry #3, which had 0 successes
    # We need to go back to previous runs
    
# The issue is we've been overwriting files. Let me check logs to reconstruct
print("\nChecking logs directory...")
log_files = [f for f in os.listdir('logs_new') if f.startswith('url_')]
print(f"Found {len(log_files)} log files")

# Best approach: Use recover_from_logs.py to extract ALL data from logs
print("\nWill use log recovery to extract all successful scrapes from logs...")
print("Note: This will take the LAST scrape's data, which is retry #3 (0 successes)")
print("\nWe need to restore logs from ALL previous runs to get all 164 successes.")
print("\nPlease advise: Do you have backups of previous output files?")
print("Or should I try a different approach?")
