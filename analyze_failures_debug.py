import pandas as pd

df = pd.read_excel('output/instagram_data_final.xlsx')

print(f"Total Rows: {len(df)}")
print(f"Status Counts:\n{df['status'].value_counts()}")

failed = df[df['status'] != 'Success']
print(f"\nFailed Entries: {len(failed)}")

for i, row in failed.iterrows():
    print(f"\n[{i+1}] URL: {row['url']}")
    print(f"    Status: {row['status']}")
    # print(f"    Error: {row['error']}") # Error column might not exist or be NaN
    print(f"    Likes: {row['likes']}")
    
    # Check if we can infer 'Hidden' from existing data or if it's a hard error
    if row['likes'] == 0:
        pass
