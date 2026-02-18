import pandas as pd

try:
    file_path = 'final_output/Instagram_Final_Updated_114.xlsx'
    # Try reading without sheet name first to see available sheets
    xl = pd.ExcelFile(file_path)
    print(f"Sheet names: {xl.sheet_names}")
    
    # Read the first sheet
    df = pd.read_excel(file_path, sheet_name=xl.sheet_names[0])
    print(f"\nColumns in {xl.sheet_names[0]}:")
    print(df.columns.tolist())
    
    print(f"\nFirst 5 rows:")
    print(df.head().to_string())
    
except Exception as e:
    print(f"Error: {e}")
