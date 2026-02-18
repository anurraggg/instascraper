import pandas as pd

print("Creating batch4.xlsx with all successful scrapes...")

# Load the file from the earlier successful runs
# new_batch_100_urls.xlsx should have the 40 successes from the first run
df_batch = pd.read_excel('output/new_batch_100_urls.xlsx')

print(f"\nLoaded new_batch_100_urls.xlsx:")
print(f"  Total: {len(df_batch)}")
print(f"  Success: {sum(df_batch['status'] == 'Success')}")
print(f"  Failed: {sum(df_batch['status'] != 'Success')}")

# Filter only successful entries
successful = df_batch[df_batch['status'] == 'Success'].copy()

print(f"\nFiltered to {len(successful)} successful entries")

# Save to batch4.xlsx
successful.to_excel('output/batch4.xlsx', index=False)
print(f"\n✅ Saved {len(successful)} successful entries to output/batch4.xlsx")

# Show sample
print("\nSample of data:")
print(successful[['url', 'likes', 'comments']].head(10).to_string())
