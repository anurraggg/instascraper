from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import re
import json
import os

# Configuration — set IG_USERNAME and IG_PASSWORD as environment variables
USERNAME = os.environ.get("IG_USERNAME", "")
PASSWORD = os.environ.get("IG_PASSWORD", "")
TARGET_URL = "https://www.instagram.com/reel/DM5F3Vzq6TN/" # First URL

def login(driver):
    print("\n🔐 Logging in as", USERNAME, "...")
    driver.get("https://www.instagram.com/")
    time.sleep(random.uniform(3, 5))
    
    try:
        if "login" not in driver.current_url and driver.find_elements(By.XPATH, "//*[@aria-label='Home']"):
            print("  ✅ Already logged in!")
            return True

        try:
            driver.find_element(By.XPATH, "//button[text()='Allow all cookies']").click()
            time.sleep(2)
        except: pass

        user_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
        user_input.clear()
        user_input.send_keys(USERNAME)
        time.sleep(random.uniform(1, 2))
        
        pass_input = driver.find_element(By.NAME, "password")
        pass_input.clear()
        pass_input.send_keys(PASSWORD)
        time.sleep(random.uniform(1, 2))
        
        pass_input.send_keys(Keys.RETURN)
        time.sleep(random.uniform(5, 8))
        
        if driver.find_elements(By.XPATH, "//div[text()='Not now']") or \
           driver.find_elements(By.XPATH, "//button[text()='Save Info']") or \
           driver.find_elements(By.XPATH, "//*[@aria-label='Home']"):
            print("  ✅ Login successful!")
            return True
            
        print("  ⚠️ Login verification needed! Please solve the challenge in the browser.")
        print("  ⏳ Waiting for you to log in... (Checking every 5s)")
        
        # Wait up to 5 minutes for manual login
        for i in range(60):
            time.sleep(5)
            if driver.find_elements(By.XPATH, "//*[@aria-label='Home']") or \
               driver.find_elements(By.XPATH, "//*[@aria-label='Search']") or \
               driver.find_elements(By.XPATH, "//img[@alt='Instagram']"):
                print("  ✅ Manual Login Detected!")
                return True
            print(f"    ...still waiting ({i*5}s)")
            
        print("  ❌ Timeout waiting for manual login.")
        return False
        
    except Exception as e:
        print(f"  ✗ Login failed: {e}")
        return False

def debug_views():
    print("\n🚀 Starting Chrome (Mobile Emulation)...")
    options = Options()
    options.add_argument('--log-level=3')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    # Mobile Emulation
    mobile_emulation = { "deviceName": "iPhone X" }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    if not login(driver):
        driver.quit()
        return

    print(f"\n🔍 Debugging URL: {TARGET_URL}")
    driver.get(TARGET_URL)
    time.sleep(5)
    
    # Scroll to trigger any lazy loading
    driver.execute_script("window.scrollTo(0, 300);")
    time.sleep(2)
    
    # Save Artifacts
    with open("debug_views.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.save_screenshot("debug_views.png")
    print("  💾 Saved debug_views.html and debug_views.png")
    
    # 5. Try Hidden API
    print("\n--- Hidden API Test ---")
    api_url = TARGET_URL.rstrip("/") + "/?__a=1&__d=dis"
    print(f"  Navigating to API URL: {api_url}")
    driver.get(api_url)
    time.sleep(2)
    
    try:
        content = driver.find_element(By.TAG_NAME, "pre").text
        print("  ✅ Found JSON content!")
        
        # Save to file
        with open("debug_api.json", "w", encoding="utf-8") as f:
            f.write(content)
        print("  💾 Saved debug_api.json")
        
        # Parse JSON
        data = json.loads(content)
        
        # Look for view count
        if "graphql" in data:
            media = data["graphql"]["shortcode_media"]
            if "video_view_count" in media:
                print(f"  ✅ Found View Count (GraphQL): {media['video_view_count']}")
            if "play_count" in media:
                print(f"  ✅ Found Play Count (GraphQL): {media['play_count']}")
                
        elif "items" in data:
            item = data["items"][0]
            if "view_count" in item:
                print(f"  ✅ Found View Count (Items): {item['view_count']}")
            if "play_count" in item:
                print(f"  ✅ Found Play Count (Items): {item['play_count']}")
                
        else:
            print("  ⚠️ JSON structure unknown, dumping keys:")
            print(data.keys())
            
    except Exception as e:
        print(f"  API Access failed: {e}")
        # Try body text if pre not found
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            print("  Dumping body text (first 500 chars):")
            print(body_text[:500])
            with open("debug_api_fail.txt", "w", encoding="utf-8") as f:
                f.write(body_text)
        except: pass
        
    driver.quit()

if __name__ == "__main__":
    debug_views()
