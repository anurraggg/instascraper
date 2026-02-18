from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pickle
import os

USERNAME = "tiyaslookbook" # Example from failed run

def debug_structure():
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
            driver.refresh()
            time.sleep(5)
            
        print(f"Visiting profile: {USERNAME}")
        driver.get(f"https://www.instagram.com/{USERNAME}/")
        time.sleep(5)
        
        # Dump Header HTML
        try:
            header = driver.find_element(By.TAG_NAME, "header")
            html = header.get_attribute("outerHTML")
            with open("debug_profile_header.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Saved header HTML.")
            
            # Print text content for quick check
            print("Header Text:")
            print(header.text)
            
        except Exception as e:
            print(f"Error finding header: {e}")
            # Dump body if header fails
            with open("debug_profile_body.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_structure()
