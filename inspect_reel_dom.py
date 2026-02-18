from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import os

def main():
    options = Options()
    options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    try:
        # Login
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)
        
        user_input = driver.find_element(By.NAME, "username")
        pass_input = driver.find_element(By.NAME, "password")
        
        user_input.send_keys(os.environ.get("IG_USERNAME", ""))
        pass_input.send_keys(os.environ.get("IG_PASSWORD", ""))
        pass_input.send_keys(Keys.ENTER)
        time.sleep(10)
        
        # Go to a Reel
        url = "https://www.instagram.com/reel/DM5F3Vzq6TN/" # Use a specific one
        print(f"Navigating to {url}")
        driver.get(url)
        time.sleep(10)
        
        # Save Source
        with open("debug_reel_source_new.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved debug_reel_source_new.html")
        
        driver.save_screenshot("debug_reel_view_new.png")
        print("Saved debug_reel_view_new.png")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
