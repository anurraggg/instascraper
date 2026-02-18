"""
Diagnostic Script
Saves the full HTML of an Instagram page for debugging
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from pathlib import Path

def main():
    print("\n" + "="*60)
    print("INSTAGRAM DIAGNOSTIC TOOL")
    print("="*60)
    
    # Setup Chrome
    print("\n🚀 Starting Chrome...")
    options = Options()
    options.add_argument('--log-level=3')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    # Login
    print("\n🔐 Please log in to Instagram manually in the browser...")
    driver.get("https://www.instagram.com/")
    print("👉 Log in to Instagram in the browser window")
    print("👉 After logging in, press ENTER here to continue...")
    input()
    
    # Go to first URL
    url = "https://www.instagram.com/p/DMsYnNeJnSp/"
    print(f"\n👉 Navigating to: {url}")
    driver.get(url)
    time.sleep(8)  # Wait for full load
    
    # Save HTML
    html = driver.page_source
    with open("instagram_debug.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print("\n✅ HTML saved to: instagram_debug.html")
    print("You can close the browser now.")
    driver.quit()

if __name__ == "__main__":
    main()
