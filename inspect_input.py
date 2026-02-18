import pandas as pd

try:
    df = pd.read_excel('input/redourls.xlsx')
    print(f"Total Rows: {len(df)}")
    print(df.head())
except Exception as e:
    print(f"Error: {e}")
