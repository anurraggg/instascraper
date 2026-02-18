import pandas as pd

INPUT_FILE = "output/instagram_profiles.xlsx"
OUTPUT_FILE = "output/instagram_bios_top50.xlsx"

def extract_bios():
    try:
        df = pd.read_excel(INPUT_FILE)
        # Take first 50
        top_50 = df.head(50).copy()
        
        # Select columns
        result = top_50[['url', 'username', 'bio']]
        
        # Save
        result.to_excel(OUTPUT_FILE, index=False)
        print(f"✅ Saved top 50 bios to {OUTPUT_FILE}")
        print(f"Rows: {len(result)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_bios()
