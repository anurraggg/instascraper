import pandas as pd
import os

directory = r'c:\Users\HP\Downloads\anti_instascraper\final_output'
files = [
    'Instagram_Data_Compiled.xlsx',
    'Instagram_Final_Complete.xlsx',
    'Instagram_Final_Merged.xlsx',
    'Instagram_Final_Updated_114.xlsx',
    'Instagram_Enriched_Complete.xlsx'
]

with open('check_results.txt', 'w') as f:
    f.write(f"{'File Name':<40} | {'Sheet Name':<20} | {'Rows':<5} | {'Columns':<5}\n")
    f.write("-" * 80 + "\n")

    for file in files:
        path = os.path.join(directory, file)
        if os.path.exists(path):
            try:
                xls = pd.ExcelFile(path)
                for sheet in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet)
                    f.write(f"{file:<40} | {sheet:<20} | {len(df):<5} | {len(df.columns):<5}\n")
            except Exception as e:
                f.write(f"{file:<40} | Error: {e}\n")
        else:
            f.write(f"{file:<40} | Not Found\n")
