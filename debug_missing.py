from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import re
import os

# Configuration — set IG_USERNAME and IG_PASSWORD as environment variables
USERNAME = os.environ.get("IG_USERNAME", "")
PASSWORD = os.environ.get("IG_PASSWORD", "")
TARGET_URL = "https://www.instagram.com/reel/DJ1nNu6ReYp/"

def login(driver):
    print("\n🔐 Logging in as", USERNAME, "...")
    driver.get("https://www.instagram.com/")
    time.sleep(random.uniform(3, 5))
    
    try:
        # Check if already logged in
        if "login" not in driver.current_url and driver.find_elements(By.XPATH, "//*[@aria-label='Home']"):
            print("  ✅ Already logged in!")
            return True

        # Accept cookies if present
        try:
            driver.find_element(By.XPATH, "//button[text()='Allow all cookies']").click()
            time.sleep(2)
        except:
            pass

        # Enter Username
        user_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        user_input.clear()
        user_input.send_keys(USERNAME)
        time.sleep(random.uniform(1, 2))
        
        # Enter Password
        pass_input = driver.find_element(By.NAME, "password")
        pass_input.clear()
        pass_input.send_keys(PASSWORD)
        time.sleep(random.uniform(1, 2))
        
        # Click Login
        pass_input.send_keys(Keys.RETURN)
        time.sleep(random.uniform(5, 8))
        
        # Check for "Save Info" or "Not Now" (means success)
        if driver.find_elements(By.XPATH, "//div[text()='Not now']") or \
           driver.find_elements(By.XPATH, "//button[text()='Save Info']") or \
           driver.find_elements(By.XPATH, "//*[@aria-label='Home']"):
            print("  ✅ Login successful!")
            return True
            
        # Check for 2FA or Challenge
        if "challenge" in driver.current_url:
            print("  ⚠️ Security Challenge detected!")
            print("  👉 Please solve the challenge in the browser window.")
            print("  👉 Press ENTER here when done...")
            input()
            return True
            
        print("  ⚠️ Login verification needed. Please check browser.")
        time.sleep(5)
        return True
        
    except Exception as e:
        print(f"  ✗ Login failed: {e}")
        return False

def debug_url():
    print("\n🚀 Starting Chrome...")
    options = Options()
    options.add_argument('--log-level=3')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    if not login(driver):
        driver.quit()
        return

    print(f"\n🔍 Debugging URL: {TARGET_URL}")
    driver.get(TARGET_URL)
    time.sleep(5)
    
    # Save Artifacts
    with open("debug_missing.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.save_screenshot("debug_missing.png")
    print("  💾 Saved debug_missing.html and debug_missing.png")
    
    # Attempt Extraction
    print("\n--- Extraction Attempt ---")
    
    # 1. Title
    print(f"Title: {driver.title}")
    
    # 2. Meta Tags
    try:
        og_title = driver.find_element(By.XPATH, "//meta[@property='og:title']").get_attribute("content")
        print(f"OG Title: {og_title}")
    except: print("OG Title: Not found")
    
    try:
        og_desc = driver.find_element(By.XPATH, "//meta[@property='og:description']").get_attribute("content")
        print(f"OG Description: {og_desc}")
    except: print("OG Description: Not found")
    
    try:
        og_url = driver.find_element(By.XPATH, "//meta[@property='og:url']").get_attribute("content")
        print(f"OG URL: {og_url}")
    except: print("OG URL: Not found")

    try:
        desc = driver.find_element(By.XPATH, "//meta[@name='description']").get_attribute("content")
        print(f"Meta Description: {desc}")
    except: print("Meta Description: Not found")

    # 3. Visible Text (Header)
    try:
        header = driver.find_element(By.TAG_NAME, "header")
        print(f"Header Text: {header.text}")
    except: print("Header: Not found")

    driver.quit()

if __name__ == "__main__":
    debug_url()
