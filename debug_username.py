from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

url = "https://www.instagram.com/reel/DIbdp6qS7oP/" # One of the failing URLs

print("🚀 Starting Chrome...")
options = Options()
options.add_argument('--log-level=3')
driver = webdriver.Chrome(options=options)
driver.maximize_window()

print("🔐 Please log in manually...")
driver.get("https://www.instagram.com/")
input("Press ENTER after login...")

print(f"Navigating to {url}...")
driver.get(url)
time.sleep(5)

page_text = driver.find_element(By.TAG_NAME, "body").text
page_source = driver.page_source

print("\n--- DEBUG INFO ---")
print(f"Title: {driver.title}")

# Strategy 1: Header link
try:
    header_link = driver.find_element(By.XPATH, "//header//a[contains(@href, '/')]")
    username = header_link.get_attribute("href").strip('/').split('/')[-1]
    print(f"Strategy 1 (Header): Found '{username}'")
except Exception as e:
    print(f"Strategy 1 (Header): Failed ({e})")

# Strategy 2: Regex
user_match = re.search(r'([a-zA-Z0-9._]+)\s*\n\s*•\s*\n\s*Follow', page_text)
if user_match:
    print(f"Strategy 2 (Regex): Found '{user_match.group(1)}'")
else:
    print("Strategy 2 (Regex): Failed")

# Strategy 3: Page Title
if 'on Instagram' in driver.title:
    username = driver.title.split('on Instagram')[0].strip().split(' ')[0]
    print(f"Strategy 3 (Title): Found '{username}'")
else:
    print("Strategy 3 (Title): Failed")

# Strategy 4: Meta tag
try:
    meta_desc = driver.find_element(By.XPATH, "//meta[@property='og:description']").get_attribute("content")
    print(f"Meta Description: {meta_desc}")
except:
    print("Meta Description: Not found")

# Save HTML
with open("debug_page.html", "w", encoding="utf-8") as f:
    f.write(page_source)
print("Saved debug_page.html")

driver.quit()
