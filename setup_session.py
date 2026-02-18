from selenium import webdriver
import pickle
import time
import os

def setup_session():
    print("Initializing Browser for Session Capture...")
    driver = webdriver.Chrome()
    
    try:
        driver.get("https://www.instagram.com/")
        print("Please log in manually in the browser.")
        print("Once logged in, press ENTER here to save cookies...")
        input()
        
        # Save cookies
        cookies = driver.get_cookies()
        with open("cookies.pkl", "wb") as f:
            pickle.dump(cookies, f)
        print(f"✅ Saved {len(cookies)} cookies to cookies.pkl")
        
        # Verify
        print("Verifying session...")
        driver.refresh()
        time.sleep(5)
        if "login" not in driver.current_url:
            print("✅ Session appears valid!")
        else:
            print("⚠️ Session might not be valid.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    setup_session()
