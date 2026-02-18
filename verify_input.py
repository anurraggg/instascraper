import pandas as pd

try:
    print("Attempting to read input/redourls.xlsx...")
    df = pd.read_excel('input/redourls.xlsx')
    print(f"Columns found: {df.columns.tolist()}")
    
    if 'URL' in df.columns:
        urls = df['URL'].dropna().tolist()
        urls = [url.strip() for url in urls if isinstance(url, str) and url.strip() and url.strip().startswith('http')]
        print(f"Successfully loaded {len(urls)} URLs.")
        print("First 3 URLs:")
        for url in urls[:3]:
            print(f" - {url}")
    else:
        print("ERROR: 'URL' column not found!")
        
except Exception as e:
    print(f"ERROR: {e}")
