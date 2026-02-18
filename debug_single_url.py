from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Setup Chrome
options = Options()
options.add_argument('--log-level=3')
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome(options=options)
driver.maximize_window()

# Test URL
url = "https://www.instagram.com/reel/DLct-isStIC/"

print("Opening Instagram...")
driver.get("https://www.instagram.com/")
print("Please log in manually...")
input("Press Enter after you've logged in...")

print(f"\nNavigating to: {url}")
driver.get(url)
time.sleep(10)

# Get page text
page_text = driver.find_element(By.TAG_NAME, "body").text

# Save to file for inspection
with open("debug_page_text.txt", "w", encoding="utf-8") as f:
    f.write(f"URL: {url}\n\n")
    f.write(page_text)

print("\nPage text saved to debug_page_text.txt")
print("\nSearching for likes and comments patterns...")

# Test regex patterns
import re

# Pattern 1: Standard likes
likes_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*likes', page_text, re.I)
if likes_match:
    print(f"Found likes (standard): {likes_match.group(1)}")
else:
    print("No standard likes pattern found")

# Pattern 2: Liked by
likes_match2 = re.search(r'Liked by\s+[^\n]+\s+and\s+(\d[\d,\.]*[KMB]?)', page_text, re.I)
if likes_match2:
    print(f"Found likes (liked by): {likes_match2.group(1)}")
else:
    print("No 'liked by' pattern found")

# Pattern 3: Comments
comments_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*comments', page_text, re.I)
if comments_match:
    print(f"Found comments: {comments_match.group(1)}")
else:
    print("No comments pattern found")

# Show first 2000 chars for manual inspection
print("\n--- First 2000 characters of page text ---")
print(page_text[:2000])

driver.quit()
