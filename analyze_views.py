import pandas as pd

def analyze_views():
    output_file = 'output/instagram_auto.xlsx'
    
    try:
        df = pd.read_excel(output_file)
        
        # Convert views to numeric, coercing errors to NaN
        df['views'] = pd.to_numeric(df['views'], errors='coerce').fillna(0)
        
        total = len(df)
        zero_views = df[df['views'] == 0]
        
        print(f"Total Rows: {total}")
        print(f"Rows with 0 Views: {len(zero_views)}")
        
        if not zero_views.empty:
            print("\nSample URLs with 0 views:")
            print(zero_views['url'].head().to_string(index=False))
            
            # Save to file for scraper
            zero_views.to_excel('output/missing_views.xlsx', index=False)
            print("\nSaved rows with 0 views to 'output/missing_views.xlsx'")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_views()
