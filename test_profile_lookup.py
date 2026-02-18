from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import os

TARGET_URL = "https://www.instagram.com/reel/DM5F3Vzq6TN/"
# Set IG_USERNAME and IG_PASSWORD as environment variables
USERNAME = os.environ.get("IG_USERNAME", "")
PASSWORD = os.environ.get("IG_PASSWORD", "")
TARGET_USERNAME = "ratnaskitchen.swad" # Hardcoded for test

def extract_number(text):
    if not text: return 0
    text = str(text).strip().upper().replace(',', '')
    multiplier = 1
    if 'K' in text: multiplier = 1000; text = text.replace('K', '')
    elif 'M' in text: multiplier = 1000000; text = text.replace('M', '')
    match = re.search(r'[\d.]+', text)
    if match: return int(float(match.group()) * multiplier)
    return 0

def test_profile_lookup():
    print(f"Testing Profile Lookup on {TARGET_URL}...")
    
    options = Options()
    options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options=options)
    
    try:
        # 1. Login
        print("Logging in...")
        driver.get("https://www.instagram.com/")
        time.sleep(3)
        
        try:
            driver.find_element(By.NAME, "username").send_keys(USERNAME)
            driver.find_element(By.NAME, "password").send_keys(PASSWORD)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(8)
        except: pass
        
        # 2. Go Directly to Profile Reels
        print(f"Navigating to profile: {TARGET_USERNAME}")
        driver.get(f"https://www.instagram.com/{TARGET_USERNAME}/reels/")
        time.sleep(5)
        
        # 3. Find Reel by Shortcode
        shortcode = "DM5F3Vzq6TN"
        print(f"Looking for shortcode: {shortcode}")
        
        found = False
        for i in range(5): # Scroll a few times
            try:
                # Look for link with shortcode
                links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{shortcode}')]")
                if links:
                    link = links[0]
                    print("✅ Found Reel Link!")
                    
                    # Get text from the parent container (usually the 'a' tag or a div inside)
                    # We might need to go up to the parent 'div' if the 'a' only contains the image
                    # But usually the 'a' tag wraps the whole tile which has the hover/overlay
                    
                    # Try 1: Link Text
                    text = link.text
                    print(f"  Link Text: {text}")
                    
                    # Try 2: Aria Label
                    aria = link.get_attribute("aria-label")
                    print(f"  Aria Label: {aria}")
                    
                    # Try 3: Inner HTML (Regex)
                    html = link.get_attribute("innerHTML")
                    
                    # Try to find number
                    views = 0
                    m = re.search(r'([\d,\.]+[KMB]?)', text)
                    if m: views = extract_number(m.group(1))
                    
                    if views == 0 and aria:
                        m = re.search(r'([\d,\.]+[KMB]?)', aria)
                        if m: views = extract_number(m.group(1))
                        
                    if views == 0:
                        # Look for number in HTML (e.g. <span class="x">7,550</span>)
                        # This is risky but might work
                        m = re.search(r'>\s*([\d,\.]+[KMB]?)\s*<', html)
                        if m: views = extract_number(m.group(1))
                        
                    if views > 0:
                        print(f"✅ Extracted Views: {views}")
                        found = True
                        break
                    else:
                        print("⚠️ Found link but could not extract views")
                        
            except Exception as e:
                print(f"Error searching: {e}")
                
            driver.execute_script("window.scrollBy(0, 1000)")
            time.sleep(2)
            
        if not found:
            print("❌ Reel not found in grid")
            driver.save_screenshot("debug_profile_fail.png")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_profile_lookup()
