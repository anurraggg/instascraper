import pandas as pd
from pathlib import Path
import shutil

print("="*60)
print("CREATING FINAL EXCEL FILE")
print("="*60)

source_file = 'final_output/Instagram_Data_Compiled.xlsx'
dest_file = 'final_output/Instagram_Final_Complete.xlsx'

try:
    # Read the compiled file to ensure it's valid
    df_posts = pd.read_excel(source_file, sheet_name='Posts_Reels')
    df_profiles = pd.read_excel(source_file, sheet_name='Profiles')
    
    print(f"✓ Loaded Source Data:")
    print(f"  Posts/Reels: {len(df_posts)} rows")
    print(f"  Profiles: {len(df_profiles)} rows")
    
    # Save to new file
    with pd.ExcelWriter(dest_file, engine='openpyxl') as writer:
        df_posts.to_excel(writer, sheet_name='Posts_Reels', index=False)
        df_profiles.to_excel(writer, sheet_name='Profiles', index=False)
        
    print(f"\n✅ Created New File: {dest_file}")
    
except Exception as e:
    print(f"✗ Error creating new file: {e}")
