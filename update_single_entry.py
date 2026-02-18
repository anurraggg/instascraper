import pandas as pd
import os

file_path = 'final_output/Instagram_Data_Compiled.xlsx'
target_url = 'https://www.instagram.com/p/DMsYnNeJnSp/'
new_views = 14600

print(f"Loading {file_path}...")
try:
    df = pd.read_excel(file_path, sheet_name='Posts_Reels')
    
    # Check current value
    row = df[df['url'] == target_url]
    if not row.empty:
        print(f"Current value: {row.iloc[0]['views']} (Status: {row.iloc[0]['status']})")
        
        # Update
        df.loc[df['url'] == target_url, 'views'] = new_views
        df.loc[df['url'] == target_url, 'status'] = 'Success'
        
        print(f"Updated value to: {new_views} (Status: Success)")
        
        # Save back
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name='Posts_Reels', index=False)
            # We need to preserve the other sheet 'Profiles'
            # But mode='a' with if_sheet_exists='replace' only replaces the named sheet.
            # However, to be safe, let's read both and write both.
            
    else:
        print(f"URL not found: {target_url}")

except Exception as e:
    print(f"Error: {e}")

# Re-saving with both sheets to be safe
try:
    df_posts = pd.read_excel(file_path, sheet_name='Posts_Reels')
    df_profiles = pd.read_excel(file_path, sheet_name='Profiles')
    
    # Apply update again to be sure (in memory)
    df_posts.loc[df_posts['url'] == target_url, 'views'] = new_views
    df_posts.loc[df_posts['url'] == target_url, 'status'] = 'Success'
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df_posts.to_excel(writer, sheet_name='Posts_Reels', index=False)
        df_profiles.to_excel(writer, sheet_name='Profiles', index=False)
    print("Successfully saved both sheets.")
    
except Exception as e:
    print(f"Error saving full file: {e}")
