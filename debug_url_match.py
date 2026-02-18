import pandas as pd

print("Loading input...")
input_df = pd.read_excel('input/INSTAURL.xlsx')
input_urls = input_df.iloc[:, 0].dropna().tolist()
print(f"Input URLs: {len(input_urls)}")
print(f"First 3 Input: {input_urls[:3]}")

print("\nLoading output...")
output_df = pd.read_excel('output/instagram_data_new.xlsx')
output_urls = output_df['url'].tolist()
print(f"Output URLs: {len(output_urls)}")
print(f"First 3 Output: {output_urls[:3]}")

print("\nChecking exact match for first output URL in input...")
first_out = output_urls[0]
if first_out in input_urls:
    print(f"Match found for {first_out}")
else:
    print(f"NO MATCH for {first_out}")
    # Inspect close matches?
    for u in input_urls:
        if u in first_out or first_out in u:
             print(f"  Partial match: '{u}' vs '{first_out}'")
