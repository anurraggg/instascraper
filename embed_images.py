import pandas as pd
import xlsxwriter
import os
import argparse


INPUT_FILE = "output/instagram_media.xlsx"
OUTPUT_FILE = "output/instagram_media_visual.xlsx"
IMAGE_COL = "Snapshot Image"

def embed_images(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    print("="*60)
    print("EMBEDDING IMAGES IN EXCEL")
    print("="*60)

    try:
        df = pd.read_excel(input_file)
        print(f"✓ Loaded {len(df)} rows from {input_file}")
    except Exception as e:
        print(f"✗ Error loading file: {e}")
        return

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    
    # Convert the dataframe to an XlsxWriter Excel object.
    # We'll leave space for the image column
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    
    workbook  = writer.book
    worksheet = writer.sheets['Sheet1']
    
    # Get the dimensions of the dataframe.
    (max_row, max_col) = df.shape

    # Set the column width and row height
    worksheet.set_column(max_col, max_col, 20) # Set width for image column
    
    # Add a header for the image column
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
    worksheet.write(0, max_col, IMAGE_COL, header_format)

    print("  Processing rows...")
    
    for i, row in df.iterrows():
        # Excel rows are 0-indexed, but header is row 0, so data starts at row 1.
        # i is 0-indexed from dataframe, so excel row is i + 1
        excel_row = i + 1
        
        # Set row height to accommodate image (e.g., 100 pixels)
        worksheet.set_row(excel_row, 100)
        
        snapshot_path = row.get('snapshot_path')
        
        if pd.notna(snapshot_path) and isinstance(snapshot_path, str) and os.path.exists(snapshot_path):
            try:
                # Insert the image
                worksheet.insert_image(excel_row, max_col, snapshot_path, {
                    'x_scale': 0.5, 
                    'y_scale': 0.5, 
                    'object_position': 1, # Move and size with cells
                    'x_offset': 5,
                    'y_offset': 5
                })
            except Exception as e:
                print(f"    ⚠️ Error inserting image for row {i}: {e}")
        else:
            # Write "No Image" if missing
            worksheet.write(excel_row, max_col, "No Image")

    writer.close()
    print(f"\n✅ Done! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embed images in Excel")
    parser.add_argument("--input", default=INPUT_FILE, help="Path to input Excel file")
    parser.add_argument("--output", default=OUTPUT_FILE, help="Path to output Excel file")
    args = parser.parse_args()
    
    embed_images(input_file=args.input, output_file=args.output)
