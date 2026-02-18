import pandas as pd

INPUT_FILE = "output/instagram_profiles.xlsx"
OUTPUT_FILE = "output/instagram_bios_next50.xlsx"

def extract_next_bios():
    try:
        df = pd.read_excel(INPUT_FILE)
        # Take next 50 (index 50 to 100)
        next_50 = df.iloc[50:100].copy()
        
        # Select columns
        result = next_50[['url', 'username', 'bio']]
        
        # Save
        result.to_excel(OUTPUT_FILE, index=False)
        print(f"✅ Saved next 50 bios to {OUTPUT_FILE}")
        print(f"Rows: {len(result)}")
        print(f"Range: {next_50.index.min()} - {next_50.index.max()}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_next_bios()
