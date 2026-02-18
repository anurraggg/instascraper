import pandas as pd

try:
    df = pd.read_excel('input/redourls.xlsx')
    print("Columns:", df.columns.tolist())
    print(df.head().to_string())
except Exception as e:
    print(f"Error: {e}")
