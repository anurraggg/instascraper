from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

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

def manual_test():
    print("Initializing Browser...")
    options = Options()
    options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://www.instagram.com/")
        print("BROWSER_READY") # Signal to agent
        print("Please log in manually in the browser.")
        print("Waiting for input...")
        input() # Wait for agent to send newline
        
        print("Proceeding to target URL...")
        driver.get(TARGET_URL)
        time.sleep(5)
        
        # 1. Try Direct Page Source
        print("Checking Page Source...")
        html = driver.page_source
        text = driver.find_element(By.TAG_NAME, "body").text
        
        # Look for "plays"
        m = re.search(r'(\d[\d,\.]*[KMB]?)\s*plays', text, re.I)
        if m:
            print(f"✅ Found Views (Direct Text): {extract_number(m.group(1))}")
        else:
            print("❌ No 'plays' text found.")
            
        # Look for "view_count" in JSON
        m = re.search(r'"view_count":\s*(\d+)', html)
        if m:
            print(f"✅ Found Views (JSON): {m.group(1)}")
        else:
            print("❌ No 'view_count' in JSON found.")
            
        # 2. Try Profile Lookup (Fallback)
        if "friesandvogue" in driver.current_url or True: # Always try if direct failed
            print("Trying Profile Lookup...")
            driver.get("https://www.instagram.com/friesandvogue/reels/")
            time.sleep(5)
            
            shortcode = "DM5F3Vzq6TN"
            found = False
            for i in range(20):
                try:
                    links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{shortcode}')]")
                    if links:
                        print("✅ Found Reel in Grid!")
                        print(f"Text: {links[0].text}")
                        found = True
                        break
                except: pass
                driver.execute_script("window.scrollBy(0, 1000)")
                time.sleep(1)
                
            if not found:
                print("❌ Reel not found in grid after scrolling.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Closing in 30 seconds...")
        time.sleep(30)
        driver.quit()

if __name__ == "__main__":
    manual_test()
