import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import random
import re
import os

# Set IG_USERNAME and IG_PASSWORD as environment variables
USERNAME = os.environ.get("IG_USERNAME", "")
PASSWORD = os.environ.get("IG_PASSWORD", "")
INPUT_FILE = "input/redourls.xlsx"

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
            
        if "challenge" in driver.current_url:
            print("  ⚠️ Security Challenge detected! Solve it manually.")
            input("Press ENTER when done...")
            return True
            
        print("  ⚠️ Login verification needed. Please check browser.")
        time.sleep(5)
        return True
        
    except Exception as e:
        print(f"  ✗ Login failed: {e}")
        return False

def check_url(driver, url, index):
    print(f"\n[{index}] Checking URL: {url}")
    driver.get(url)
    time.sleep(5)
    
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Search for views
        views = "Not Found"
        m = re.search(r'(\d[\d,\.]*[KMB]?)\s*(?:views?|plays?)', body_text, re.I)
        if m:
            views = m.group(1)
            print(f"  ✅ Found Views in Text: {views}")
        else:
            print("  ❌ No views found in Text")
            
        # Search for likes to compare
        likes = "Not Found"
        m_likes = re.search(r'(\d[\d,\.]*[KMB]?)\s*likes?', body_text, re.I)
        if m_likes:
            likes = m_likes.group(1)
            print(f"  👍 Found Likes in Text: {likes}")
            
        # Save text dump for this URL
        with open(f"debug_text_{index}.txt", "w", encoding="utf-8") as f:
            f.write(body_text)
            
    except Exception as e:
        print(f"  Error: {e}")

def main():
    print("Reading input file...")
    df = pd.read_excel(INPUT_FILE)
    urls = df.iloc[:, 0].tolist()[:5] # First 5 URLs
    
    print("\n🚀 Starting Chrome...")
    options = Options()
    options.add_argument('--log-level=3')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    if login(driver):
        for i, url in enumerate(urls):
            check_url(driver, url, i)
            
    driver.quit()

if __name__ == "__main__":
    main()
