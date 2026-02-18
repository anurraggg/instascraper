from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import time
import random
import os

# Configuration — set IG_USERNAME and IG_PASSWORD as environment variables
USERNAME = os.environ.get("IG_USERNAME", "")
PASSWORD = os.environ.get("IG_PASSWORD", "")
TARGET_URL = "https://www.instagram.com/reel/DM5F3Vzq6TN/"

def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response

def debug_network():
    print("\n🚀 Starting Chrome with Network Logging...")
    
    options = Options()
    options.add_argument('--log-level=3')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    # Enable Performance Logging
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    # Keep browser open
    options.add_experimental_option("detach", True)
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    print("  ✅ Browser Window Launched!")
    
    # Login Check
    print(f"  Navigating to Login Page...")
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)
    
    print("  ⚠️ Please manually log in!")
    print("  ⏳ Waiting for Home Screen... (Checking every 5s)")
    
    for i in range(60):
        time.sleep(5)
        # Stricter checks for Home screen
        if driver.find_elements(By.XPATH, "//*[@aria-label='Home']") or \
           driver.find_elements(By.XPATH, "//*[@aria-label='Search']") or \
           driver.find_elements(By.XPATH, "//*[@aria-label='Messenger']") or \
           driver.find_elements(By.XPATH, "//*[@aria-label='Direct']"):
            print("  ✅ Login Detected (Home Screen found)!")
            break
        print(f"    ...waiting ({i*5}s)")
        
    print(f"  Navigating to Target URL: {TARGET_URL}...")
    driver.get(TARGET_URL)
    time.sleep(10) # Wait for network requests
    
    print("  Analyzing Network Logs...")
    logs = driver.get_log('performance')
    
    found_views = False
    
    for entry in logs:
        try:
            log_message = json.loads(entry['message'])['message']
            
            # We are interested in Network.responseReceived or Network.requestWillBeSent
            # But mostly we need the BODY of the response, which requires CDP command 'Network.getResponseBody'
            # However, standard Selenium log only gives headers/metadata usually.
            # BUT, sometimes the data is in the 'params' if it's small, or we filter for specific GraphQL.
            
            method = log_message.get('method')
            
            # Filter for GraphQL or API calls
            if method == 'Network.responseReceived':
                url = log_message['params']['response']['url']
                if "graphql" in url or "api/v1" in url:
                    # print(f"  Captured API Call: {url}")
                    
                    # To get body, we need to use CDP
                    request_id = log_message['params']['requestId']
                    try:
                        response_body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                        body_content = response_body['body']
                        
                        if "video_view_count" in body_content or "play_count" in body_content:
                            print(f"\n  ✅ Found Potential Data in: {url}")
                            
                            # Parse JSON
                            data = json.loads(body_content)
                            
                            # Recursive search for keys
                            def find_views(node):
                                if isinstance(node, dict):
                                    for k, v in node.items():
                                        if k == 'video_view_count':
                                            print(f"    🎯 FOUND video_view_count: {v}")
                                        elif k == 'play_count':
                                            print(f"    🎯 FOUND play_count: {v}")
                                        elif isinstance(v, (dict, list)):
                                            find_views(v)
                                elif isinstance(node, list):
                                    for i in node:
                                        find_views(i)
                                        
                            find_views(data)
                            found_views = True
                            
                    except Exception as e:
                        # Body might be missing or empty
                        pass
                        
        except Exception as e:
            pass
            
    if not found_views:
        print("  ❌ No view counts found in network logs.")
        
    print("\n  ℹ Script finished. Browser will remain open.")
    input("  Press Enter to close the script (browser may stay open)...")
    driver.quit()

if __name__ == "__main__":
    debug_network()
