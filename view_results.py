import pandas as pd

df = pd.read_excel('output/instagram_data.xlsx')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 60)

print(df)
print('\n' + '='*80)
print('SUMMARY:')
print(f'Total Likes: {df["likes"].sum():,}')
print(f'Total Comments: {df["comments"].sum():,}')
print(f'Total Views: {df["views"].sum():,}')
print(f'Successful: {(df["status"] == "Success").sum()}/{len(df)}')
