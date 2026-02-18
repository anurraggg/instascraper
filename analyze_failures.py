import pandas as pd
import os

def analyze_failures():
    output_file = 'output/instagram_data.xlsx'
    
    if not os.path.exists(output_file):
        print(f"File not found: {output_file}")
        return

    try:
        df = pd.read_excel(output_file)
        
        # Filter for failures
        failures = df[df['status'] != 'Success']
        
        print(f"\nTotal Failures: {len(failures)}")
        print("="*60)
        
        if len(failures) == 0:
            print("No failures found!")
            return

        # Categorize failures
        profile_urls = failures[~failures['url'].str.contains('/p/|/reel/|/tv/', regex=True)]
        post_urls = failures[failures['url'].str.contains('/p/|/reel/|/tv/', regex=True)]
        
        print(f"\nCategory Breakdown:")
        print(f"  - Profile URLs: {len(profile_urls)}")
        print(f"  - Post/Reel URLs: {len(post_urls)}")
        
        print("\n" + "="*60)
        print("PROFILE URL ANALYSIS")
        print("="*60)
        if not profile_urls.empty:
            # Check if followers were extracted
            with_followers = profile_urls[profile_urls['followers'] > 0]
            print(f"Profile URLs with followers extracted: {len(with_followers)} / {len(profile_urls)}")
            
            print("\nExample Profile URLs:")
            for url in profile_urls['url'].head(5):
                print(f"  - {url}")
        else:
            print("No profile URLs failed.")

        print("\n" + "="*60)
        print("POST/REEL URL ANALYSIS")
        print("="*60)
        if not post_urls.empty:
            print("\nFailed Post URLs:")
            for index, row in post_urls.iterrows():
                print(f"URL: {row['url']}")
                print(f"Error: {row['error']}")
                print(f"Data Found: Likes={row['likes']}, Comments={row['comments']}, Views={row['views']}")
                print("-" * 30)
        else:
            print("No post URLs failed.")
            
    except Exception as e:
        print(f"Error analyzing file: {e}")

if __name__ == "__main__":
    analyze_failures()
