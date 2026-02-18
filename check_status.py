import pandas as pd
import os

def check_status():
    input_file = 'input/redourls.xlsx'
    output_file = 'output/instagram_auto.xlsx'
    
    if os.path.exists(output_file):
        try:
            df = pd.read_excel(output_file)
            print(f"Total Rows: {len(df)}")
            print("-" * 20)
            print("Non-empty counts:")
            for col in df.columns:
                print(f"{col}: {df[col].count()}")
            print("-" * 20)
            print("First row data:")
            print(df.iloc[0].to_dict())
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Output file not found")

if __name__ == "__main__":
    check_status()
