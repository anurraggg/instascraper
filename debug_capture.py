from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# URL 1
url = "https://www.instagram.com/reel/DM4_qshB3le/?igsh=aDdkcW"

print("🚀 Starting Chrome...")
options = Options()
# options.add_argument('--headless') # Keep visible to see what happens
driver = webdriver.Chrome(options=options)
driver.maximize_window()

print("🔐 Please log in manually if needed...")
driver.get("https://www.instagram.com/")
print("👉 Press ENTER after logging in...")
input()

print(f"📄 Navigating to {url}...")
driver.get(url)
time.sleep(5)

print("💾 Saving HTML...")
with open("debug_page_source.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

print("✅ Saved to debug_page_source.html")
driver.quit()
