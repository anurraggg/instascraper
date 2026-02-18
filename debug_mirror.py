from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

# Target Shortcode from https://www.instagram.com/reel/DM5F3Vzq6TN/
SHORTCODE = "DM5F3Vzq6TN"
# Picuki format: https://www.picuki.com/media/{shortcode} is not direct.
# We need to search or use a known format. 
# Picuki uses internal IDs often, but let's try searching or a different mirror.
# Let's try 'dumpoir' or 'greatfon' (now 'dumpor')?
# Actually, let's try 'instagram.com' via 'google cache'? No.

# Let's try 'publer.io'
# https://publer.io/tools/instagram-downloader
# This one requires inputting the URL and clicking a button.
# We need to automate the interaction.
MIRROR_URL = "https://publer.io/tools/instagram-downloader"
TARGET_IG_URL = "https://www.instagram.com/reel/DM5F3Vzq6TN/"

def debug_mirror():
    print(f"\n🚀 Checking Mirror: {MIRROR_URL}")
    
    options = Options()
    # options.add_argument('--headless') # Keep visible for debugging interaction
    options.add_argument('--log-level=3')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(MIRROR_URL)
        time.sleep(5)
        
        # Find input field
        print("  Finding input field...")
        input_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Paste']")
        input_field.clear()
        input_field.send_keys(TARGET_IG_URL)
        
        # Find button
        print("  Clicking download/check button...")
        btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        btn.click()
        
        print("  ⏳ Waiting for results...")
        time.sleep(10)
        
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Look for views
        # Imginn usually shows "X views" or similar
        print("\n--- Page Text Analysis ---")
        
        # Regex for views
        m = re.search(r'(\d[\d,\.]*[KMB]?)\s*views?', body_text, re.I)
        if m:
            print(f"  ✅ Found Views: {m.group(1)}")
        else:
            print("  ❌ Views not found in text.")
            
        # Regex for plays
        m = re.search(r'(\d[\d,\.]*[KMB]?)\s*plays?', body_text, re.I)
        if m:
            print(f"  ✅ Found Plays: {m.group(1)}")
            
        # Dump text for debugging
        print("\n--- First 500 chars of body ---")
        print(body_text[:500])
        
    except Exception as e:
        print(f"  Error: {e}")
        
    driver.quit()

if __name__ == "__main__":
    debug_mirror()
