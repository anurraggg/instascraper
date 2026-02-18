from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time
import random
import os

# Configuration — set IG_USERNAME and IG_PASSWORD as environment variables
USERNAME = os.environ.get("IG_USERNAME", "")
PASSWORD = os.environ.get("IG_PASSWORD", "")

def export_cookies():
    print("\n🚀 Starting Chrome to export cookies...")
    options = Options()
    options.add_argument('--log-level=3')
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    print(f"\n🔐 Logging in as {USERNAME}...")
    driver.get("https://www.instagram.com/")
    time.sleep(random.uniform(3, 5))
    
    try:
        # Accept cookies
        try:
            driver.find_element(By.XPATH, "//button[text()='Allow all cookies']").click()
            time.sleep(2)
        except: pass

        user_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
        user_input.send_keys(USERNAME)
        time.sleep(1)
        
        pass_input = driver.find_element(By.NAME, "password")
        pass_input.send_keys(PASSWORD)
        time.sleep(1)
        
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(random.uniform(5, 8))
        
        # Check success
        if driver.find_elements(By.XPATH, "//*[@aria-label='Home']") or \
           driver.find_elements(By.XPATH, "//button[text()='Not Now']"):
            print("✅ Login successful!")
            
            # Save cookies
            cookies = driver.get_cookies()
            pickle.dump(cookies, open("cookies.pkl", "wb"))
            print("  💾 Saved cookies to 'cookies.pkl'")
            
        else:
            print("  ⚠ Login might have failed or needs verification.")
            # Save anyway just in case
            cookies = driver.get_cookies()
            pickle.dump(cookies, open("cookies.pkl", "wb"))
            print("  💾 Saved cookies (potentially incomplete) to 'cookies.pkl'")

    except Exception as e:
        print(f"✗ Error: {e}")
    
    driver.quit()

if __name__ == "__main__":
    export_cookies()
