import pandas as pd
import scraper_media

# Create subset input
try:
    df = pd.read_excel("input/redourls.xlsx")
    subset = df.head(3)
    subset.to_excel("input/test_media_input.xlsx", index=False)
    print("Created test input file.")
except Exception as e:
    print(f"Error creating test input: {e}")
    exit(1)

# Run scraper on subset
print("Running scraper on subset...")
scraper_media.main(input_file="input/test_media_input.xlsx", output_file="output/test_media_output.xlsx")

# Verify output
try:
    out_df = pd.read_excel("output/test_media_output.xlsx")
    print("\nVerification Results:")
    print(out_df[['shortcode', 'media_url', 'snapshot_path', 'status']])
    
    success_count = len(out_df[out_df['status'] == 'Success'])
    print(f"\nSuccess: {success_count}/{len(out_df)}")
except Exception as e:
    print(f"Error verifying output: {e}")
