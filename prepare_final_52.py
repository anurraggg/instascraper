import pandas as pd

# Read the results from the 114 retry
df = pd.read_csv('retry_failed_114_results.csv')

# Filter for failures
failed_df = df[df['status'] == 'Failed']

print(f"Found {len(failed_df)} failed URLs.")

# Save to new CSV
output_file = 'retry_failed_52.csv'
failed_df[['url']].to_csv(output_file, index=False)

print(f"Saved failed URLs to {output_file}")
