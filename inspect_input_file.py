import pandas as pd

df = pd.read_excel('input/INSTAURL.xlsx')
print(f"Columns: {df.columns.tolist()}")
print("First 5 rows:")
print(df.head())
