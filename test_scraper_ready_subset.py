from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import random
import os

# Configuration — set IG_USERNAME and IG_PASSWORD as environment variables
USERNAME = os.environ.get("IG_USERNAME", "")
PASSWORD = os.environ.get("IG_PASSWORD", "")
TARGET_URL = "https://www.instagram.com/reel/DM5F3Vzq6TN/"

def extract_number(text):
    if not text: return 0
    text = str(text).strip().upper().replace(',', '')
    multiplier = 1
    if 'K' in text: multiplier = 1000; text = text.replace('K', '')
    elif 'M' in text: multiplier = 1000000; text = text.replace('M', '')
    match = re.search(r'[\d.]+', text)
    if match: return int(float(match.group()) * multiplier)
    return 0

def login(driver):
    print("Logging in...")
    driver.get("https://www.instagram.com/")
    time.sleep(5)
    try:
        driver.find_element(By.NAME, "username").send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(10)
    except: pass

def test_scraper_ready():
    print("Testing scraper_ready logic...")
    options = Options()
    options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options=options)
    
    try:
        login(driver)
        
        url = TARGET_URL
        print(f"Processing: {url}")
        driver.get(url)
        time.sleep(5)
        
        # Profile Lookup Logic from scraper_ready.py
        username = ''
        # Strategy 1: Article Header
        try:
            links = driver.find_elements(By.XPATH, "//article//header//a")
            for link in links:
                href = link.get_attribute("href")
                if href:
                    username = href.strip('/').split('/')[-1]
                    print(f"Found username: {username}")
                    break
        except: pass
        
        if not username:
            # Fallback hardcode for test
            username = "ratnaskitchen.swad" 
            print(f"Using fallback username: {username}")

        if username:
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(f"https://www.instagram.com/{username}/reels/")
            time.sleep(6)
            
            shortcode = "DM5F3Vzq6TN"
            print(f"Looking for shortcode: {shortcode}")
            
            found = False
            for i in range(20): # Scroll 20 times
                try:
                    links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{shortcode}')]")
                    if links:
                        print("✅ Found reel link!")
                        link = links[0]
                        print(f"Text: {link.text}")
                        
                        # Inner HTML check
                        html = link.get_attribute("innerHTML")
                        m = re.search(r'>\s*([\d,\.]+[KMB]?)\s*<', html)
                        if m:
                            print(f"✅ Found views in HTML: {extract_number(m.group(1))}")
                            found = True
                            break
                            
                        # Text check
                        m = re.search(r'([\d,\.]+[KMB]?)', link.text)
                        if m:
                            print(f"✅ Found views in Text: {extract_number(m.group(1))}")
                            found = True
                            break
                            
                except Exception as e:
                    print(f"Error: {e}")
                    
                driver.execute_script("window.scrollBy(0, 1000)")
                time.sleep(1.5)
                
            if not found:
                print("❌ Not found after scrolling")
                
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_scraper_ready()
