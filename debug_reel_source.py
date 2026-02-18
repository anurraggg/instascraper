from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import json
import os

# Configuration — set IG_USERNAME and IG_PASSWORD as environment variables
USERNAME = os.environ.get("IG_USERNAME", "")
PASSWORD = os.environ.get("IG_PASSWORD", "")
TARGET_URL = "https://www.instagram.com/reel/DM5F3Vzq6TN/"

def debug_reel_source():
    print(f"Debugging {TARGET_URL}...")
    
    options = Options()
    options.add_argument('--log-level=3')
    # options.add_argument('--headless') # Keep visible to see what happens
    driver = webdriver.Chrome(options=options)
    
    try:
        # 1. Login
        print("Logging in...")
        driver.get("https://www.instagram.com/")
        time.sleep(5)
        
        try:
            driver.find_element(By.NAME, "username").send_keys(USERNAME)
            driver.find_element(By.NAME, "password").send_keys(PASSWORD)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(10)
        except: pass
        
        # 2. Go to Reel
        print("Navigating to Reel...")
        driver.get(TARGET_URL)
        time.sleep(8)
        
        # 3. Capture Data
        print("Capturing data...")
        
        # Screenshot
        driver.save_screenshot("debug_reel_page.png")
        
        # Page Source
        html = driver.page_source
        with open("debug_reel_source.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        # Text Content
        text = driver.find_element(By.TAG_NAME, "body").text
        with open("debug_reel_text.txt", "w", encoding="utf-8") as f:
            f.write(text)
            
        # Search for keywords
        print("\n--- SEARCH RESULTS ---")
        
        # Regex for numbers followed by "plays" or "views"
        matches = re.findall(r'([\d,\.]+[KMB]?)\s*(?:plays|views)', text, re.I)
        print(f"Text Matches (plays/views): {matches}")
        
        # Search in HTML for "view_count" or similar
        json_matches = re.findall(r'"view_count":\s*(\d+)', html)
        print(f"JSON 'view_count' matches: {json_matches}")
        
        play_matches = re.findall(r'"play_count":\s*(\d+)', html)
        print(f"JSON 'play_count' matches: {play_matches}")
        
        # Look for specific numbers if we know ground truth is ~7550
        specific = re.findall(r'(7[\d,\.]*5[\d,\.]*)', html)
        print(f"Specific number matches (7...5...): {specific[:10]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_reel_source()
