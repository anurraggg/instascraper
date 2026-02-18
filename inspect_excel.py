import pandas as pd
import os

file_path = 'output/instagram_data_new.xlsx'
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    print(f"Rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    print("\nSample Data:")
    print(df[['url', 'likes', 'comments', 'views']].head(10))
    print("\nStatus Counts:")
    print(df['status'].value_counts())
else:
    print(f"File not found: {file_path}")
