"""
Deep Debug Script
Captures Title, HTML, Screenshot, and attempts to find Username via Selenium.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

def main():
    url = "https://www.instagram.com/reel/DDtZ0u7y_eQ/"
    print(f"Deep Debugging: {url}")
    
    options = Options()
    options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://www.instagram.com/")
        print("Please log in if needed, then press ENTER.")
        input()
        
        driver.get(url)
        time.sleep(8) # Wait longer for render
        
        print("\n--- PAGE INFO ---")
        print(f"Title: {driver.title}")
        print(f"URL: {driver.current_url}")
        
        # Screenshot
        driver.save_screenshot("debug_screenshot.png")
        print("Saved debug_screenshot.png")
        
        # HTML
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved debug_page.html")
        
        # Try to find Username
        print("\n--- USERNAME SEARCH ---")
        
        # 1. Header Link
        try:
            links = driver.find_elements(By.XPATH, "//header//a")
            print(f"Found {len(links)} links in header.")
            for l in links:
                print(f"  Link: {l.get_attribute('href')} | Text: {l.text}")
        except:
            print("Error searching header.")
            
        # 2. Meta Title
        try:
            meta = driver.find_element(By.XPATH, "//meta[@property='og:title']")
            print(f"Meta Title: {meta.get_attribute('content')}")
        except:
            print("Meta Title not found.")
            
        # 3. Canonical Link
        try:
            link = driver.find_element(By.XPATH, "//link[@rel='canonical']")
            print(f"Canonical: {link.get_attribute('href')}")
        except:
            print("Canonical not found.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
