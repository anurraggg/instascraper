from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os

# Set IG_USERNAME and IG_PASSWORD as environment variables
USERNAME = os.environ.get("IG_USERNAME", "")
PASSWORD = os.environ.get("IG_PASSWORD", "")
TARGET_PROFILE = "friesandvogue"

def debug_hrefs():
    options = Options()
    options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options=options)
    
import pickle
import os

def debug_hrefs():
    options = Options()
    options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options=options)
    
    try:
        # Load Cookies
        print("Loading session...")
        driver.get("https://www.instagram.com/")
        time.sleep(3)
        
        if os.path.exists("cookies.pkl"):
            with open("cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    driver.add_cookie(cookie)
            print("Cookies loaded.")
            driver.refresh()
            time.sleep(5)
        
        # Go to Reels
        url = f"https://www.instagram.com/{TARGET_PROFILE}/reels/"
        print(f"Going to {url}")
        driver.get(url)
        time.sleep(5)
        
        print("Scanning links...")
        all_hrefs = set()
        
        with open("debug_hrefs.txt", "w", encoding="utf-8") as f:
            for i in range(100):
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if href and ('/reel/' in href or '/p/' in href):
                        if href not in all_hrefs:
                            all_hrefs.add(href)
                            f.write(href + "\n")
                            print(f"Found: {href}")
                
                driver.execute_script("window.scrollBy(0, 1000)")
                time.sleep(1)
                if i % 10 == 0: print(f"Scroll {i}/100")
                
        print(f"Total unique links found: {len(all_hrefs)}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_hrefs()
