import pandas as pd

# Read the results
df = pd.read_csv('final_retry_results.csv')

# Filter for failures
failed_df = df[df['status'] == 'Failed']

print(f"Found {len(failed_df)} failed URLs.")

# Save to new CSV
output_file = 'retry_failed_114.csv'
failed_df[['url']].to_csv(output_file, index=False)

print(f"Saved failed URLs to {output_file}")
