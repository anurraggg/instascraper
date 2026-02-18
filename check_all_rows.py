import pandas as pd
import os
import glob

def check_rows():
    print("Checking Excel Row Counts...")
    files = glob.glob("**/*.xlsx", recursive=True)
    
    for f in files:
        if "lock" in f or "~" in f: continue
        try:
            df = pd.read_excel(f)
            print(f"{f}: {len(df)} rows")
            if "views" in df.columns:
                non_zero = df[df['views'] > 0].shape[0]
                print(f"  -> Non-zero views: {non_zero}")
        except Exception as e:
            print(f"{f}: Error {e}")

if __name__ == "__main__":
    check_rows()
