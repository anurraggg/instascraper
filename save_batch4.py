import pandas as pd

print("Saving scraped data to batch4.xlsx...")

# Load the current scrape results
df = pd.read_excel('output/instagram_data_new.xlsx')

print(f"\nTotal URLs processed: {len(df)}")
print(f"Success: {sum(df['status'] == 'Success')}")
print(f"Failed: {sum(df['status'] != 'Success')}")

# Filter only successful entries
successful = df[df['status'] == 'Success'].copy()

print(f"\nSaving {len(successful)} successful entries to batch4.xlsx...")

# Save to batch4.xlsx
successful.to_excel('output/batch4.xlsx', index=False)

print(f"\n✅ Saved to output/batch4.xlsx")
print("\nSample of saved data:")
print(successful[['url', 'likes', 'comments']].head(10).to_string())
