from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

TARGET_URL = "https://www.instagram.com/reel/DM5F3Vzq6TN/"

def test_selenium_mobile():
    print(f"Testing Selenium Mobile (Anonymous) on {TARGET_URL}...")
    
    mobile_emulation = { "deviceName": "iPhone X" }
    options = Options()
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument('--log-level=3')
    options.add_argument('--headless') # Try headless first
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(TARGET_URL)
        time.sleep(5)
        
        # Scroll
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(2)
        
        # Get Text
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print("\n--- Page Text (First 500 chars) ---")
        print(body_text[:500])
        
        # Search for views/plays
        print("\n--- Searching for Views/Plays ---")
        
        # Regex for "10.5K plays" or "100 views"
        matches = re.findall(r'([\d,\.]+[KMB]?)\s*(?:plays?|views?)', body_text, re.I)
        print(f"Text Matches: {matches}")
        
        # Check specific elements (Aria labels often have this)
        aria_labels = [e.get_attribute("aria-label") for e in driver.find_elements(By.XPATH, "//*[@aria-label]")]
        for label in aria_labels:
            if label and ("play" in label.lower() or "view" in label.lower()):
                print(f"Aria Label Match: {label}")
                
        # Save source
        with open("debug_mobile.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_selenium_mobile()
