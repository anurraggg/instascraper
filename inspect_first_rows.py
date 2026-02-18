"""
Inspect First 200 Rows
"""
import pandas as pd

print("="*60)
print("INSPECTING FIRST 200 ROWS")
print("="*60)

try:
    file_path = 'final_output/Instagram_Final_Complete.xlsx'
    df = pd.read_excel(file_path, sheet_name='Posts_Reels')
    
    print(f"Total Rows: {len(df)}")
    
    # Inspect first 200
    subset = df.head(200)
    
    print("\nSummary of First 200 Rows:")
    print(f"  Zeros Views: {len(subset[subset['views'] == 0])}")
    print(f"  Failed Status: {len(subset[subset['status'] != 'Success'])}")
    
    print("\nFirst 10 Rows Details:")
    print(subset[['url', 'views', 'status', 'error']].head(10).to_string())
    
    print("\nRows 190-200 Details:")
    print(subset[['url', 'views', 'status', 'error']].iloc[190:200].to_string())

except Exception as e:
    print(f"Error: {e}")
