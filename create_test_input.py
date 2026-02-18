import pandas as pd
import os

# Create a small input file for testing
input_file = 'input/INSTAURL.xlsx'
test_input_file = 'input/TEST_INSTAURL.xlsx'

try:
    df = pd.read_excel(input_file)
    # Take top 3 URLs
    df_test = df.head(3)
    df_test.to_excel(test_input_file, index=False)
    print(f"Created {test_input_file} with 3 URLs for testing.")
except Exception as e:
    print(f"Error creating test file: {e}")
