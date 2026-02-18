import pandas as pd

try:
    df = pd.read_excel("output/instagram_media.xlsx")
    failed = df[df['status'] != 'Success']
    
    reel_failures = failed[failed['url'].str.contains('/reel/|/p/', na=False)]
    profile_failures = failed[~failed['url'].str.contains('/reel/|/p/', na=False)]
    
    print(f"Total Failures: {len(failed)}")
    print(f"Reel/Post Failures: {len(reel_failures)}")
    print(f"Profile Failures: {len(profile_failures)}")
    
    if len(reel_failures) > 0:
        print("\nReel Failures:")
        print(reel_failures['url'].head())
        
except Exception as e:
    print(f"Error: {e}")
