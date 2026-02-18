"""
Debug Post Scraper
Captures HTML of a post page to find correct username selectors.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from pathlib import Path

def main():
    print("\n" + "="*60)
    print("DEBUG POST SCRAPER")
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
    
    # Go to a specific post (using one from the list or a known one)
    # Using a known safe one for debugging structure
    target_post = "https://www.instagram.com/p/DDs8VowEROQ/" 
    print(f"\n👉 Navigating to {target_post}...")
    driver.get(target_post)
    time.sleep(5)
    
    # Save HTML
    html = driver.page_source
    with open("debug_post.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"\n✅ Saved HTML to debug_post.html")
    print("You can close the browser now.")
    
    driver.quit()

if __name__ == "__main__":
    main()
