import pandas as pd
try:
    df = pd.read_excel("input/redourls.xlsx")
    print(df.head())
    print(df['URL'].iloc[0])
except Exception as e:
    print(e)
