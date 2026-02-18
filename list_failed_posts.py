import pandas as pd
import os

def list_failed_posts():
    output_file = 'output/instagram_data.xlsx'
    try:
        df = pd.read_excel(output_file)
        failures = df[df['status'] != 'Success']
        post_urls = failures[failures['url'].str.contains('/p/|/reel/|/tv/', regex=True)]
        
        print("\nFailed Post/Reel URLs:")
        for index, row in post_urls.iterrows():
            print(f"- {row['url']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_failed_posts()
