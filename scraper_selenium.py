"""
Instagram Scraper using Selenium
This uses a real browser to avoid detection
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re
import json
import os
from pathlib import Path


class InstagramSeleniumScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def extract_number(self, text):
        """Extract number from text like '1.2K', '5M', '234'."""
        if not text:
            return 0
        
        text = str(text).strip().upper().replace(',', '')
        
        multiplier = 1
        if 'K' in text:
            multiplier = 1000
            text = text.replace('K', '')
        elif 'M' in text:
            multiplier = 1000000
            text = text.replace('M', '')
        elif 'B' in text:
            multiplier = 1000000000
            text = text.replace('B', '')
        
        match = re.search(r'[\d.]+', text)
        if match:
            try:
                return int(float(match.group()) * multiplier)
            except:
                return 0
        return 0
    
    def setup_driver(self):
        """Setup Chrome driver with anti-detection options."""
        print("🚀 Setting up Chrome driver...")
        
        chrome_options = Options()
        
        # Anti-detection options
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--log-level=3')
        
        # User agent
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Uncomment to run headless (invisible browser)
        # chrome_options.add_argument('--headless=new')
        
        try:
            # Try to use webdriver-manager
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"⚠ WebDriver Manager failed: {e}")
            print("Trying default Chrome...")
            # Fallback to default Chrome
            self.driver = webdriver.Chrome(options=chrome_options)
        
        # Execute CDP commands to hide automation
        try:
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                '''
            })
        except:
            pass
        
        self.wait = WebDriverWait(self.driver, 20)
        print("✅ Driver setup complete")
    
    def login(self, username, password):
        """Login to Instagram."""
        print(f"\n🔐 Logging in as {username}...")
        
        self.driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(3)
        
        try:
            # Wait for and fill username
            username_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.send_keys(username)
            time.sleep(1)
            
            # Fill password
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(password)
            time.sleep(1)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            print("⏳ Waiting for login...")
            time.sleep(8)
            
            # Check if login was successful
            current_url = self.driver.current_url
            if "challenge" in current_url or "two_factor" in current_url:
                print("\n⚠️ 2FA or challenge detected!")
                print("Please complete the verification in the browser...")
                input("Press ENTER after completing verification: ")
            
            # Handle "Save Login Info" prompt
            try:
                not_now_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Not now') or contains(text(), 'Not Now')]")
                not_now_button.click()
                time.sleep(2)
            except:
                pass
            
            # Handle "Turn on Notifications" prompt
            try:
                not_now_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now') or contains(text(), 'Not now')]")
                not_now_button.click()
                time.sleep(2)
            except:
                pass
            
            print("✅ Login successful!")
            return True
            
        except Exception as e:
            print(f"✗ Login failed: {e}")
            return False
    
    def scrape_post(self, url):
        """Scrape a single Instagram post."""
        print(f"\n{'='*60}")
        print(f"Scraping: {url}")
        print(f"{'='*60}")
        
        try:
            self.driver.get(url)
            time.sleep(5)  # Wait for page to load
            
            # Scroll to load content
            for _ in range(3):
                self.driver.execute_script("window.scrollBy(0, 300)")
                time.sleep(1)
            
            # Extract data using JavaScript
            data = self.driver.execute_script("""
                const text = document.body.innerText;
                
                // Extract likes
                const likesMatch = text.match(/(\\d[\\d,\\.]*[KMB]?)\\s*likes?/i);
                
                // Extract comments
                const commentsMatch = text.match(/(\\d[\\d,\\.]*[KMB]?)\\s*comments?/i) || 
                                     text.match(/View all (\\d[\\d,\\.]*[KMB]?)\\s*comments?/i);
                
                // Extract views
                const viewsMatch = text.match(/(\\d[\\d,\\.]*[KMB]?)\\s*views?/i);
                
                // Extract collaborators
                const collabMatch = text.match(/with\\s+@?([a-zA-Z0-9._]+)/i);
                
                return {
                    likes: likesMatch ? likesMatch[1] : null,
                    comments: commentsMatch ? commentsMatch[1] : null,
                    views: viewsMatch ? viewsMatch[1] : null,
                    collaborator: collabMatch ? collabMatch[1] : null,
                    pageText: text.substring(0, 500)
                };
            """)
            
            result = {
                'url': url,
                'likes': self.extract_number(data['likes']) if data['likes'] else 0,
                'comments': self.extract_number(data['comments']) if data['comments'] else 0,
                'views': self.extract_number(data['views']) if data['views'] else 0,
                'collaborators': data['collaborator'] if data['collaborator'] else '',
                'status': 'Success',
                'error': ''
            }
            
            print(f"✓ Likes: {result['likes']:,}")
            print(f"✓ Comments: {result['comments']:,}")
            print(f"✓ Views: {result['views']:,}")
            if result['collaborators']:
                print(f"✓ Collaborators: {result['collaborators']}")
            
            # Check if we got any data
            if result['likes'] == 0 and result['comments'] == 0 and result['views'] == 0:
                print(f"⚠ No data extracted")
                print(f"Page preview: {data['pageText'][:200]}...")
                result['status'] = 'No Data'
                result['error'] = 'Could not extract metrics'
            
            return result
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return {
                'url': url,
                'likes': 0,
                'comments': 0,
                'views': 0,
                'collaborators': '',
                'status': 'Error',
                'error': str(e)
            }
    
    def run(self):
        """Main scraping function."""
        print("\n" + "="*60)
        print("INSTAGRAM SCRAPER - SELENIUM METHOD")
        print("="*60)
        
        # Load URLs
        try:
            df = pd.read_csv('input/Instagram_URLS.csv')
            urls = df.iloc[:, 0].dropna().tolist()[1:]
            urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
            print(f"\n✓ Loaded {len(urls)} URLs")
        except Exception as e:
            print(f"✗ Error loading URLs: {e}")
            return
        
        # Setup driver
        self.setup_driver()
        
        # Login
        if not self.login(os.environ.get("IG_USERNAME", ""), os.environ.get("IG_PASSWORD", "")):
            print("✗ Cannot proceed without login")
            self.driver.quit()
            return
        
        # Scrape each URL
        results = []
        
        print(f"\n{'='*60}")
        print(f"SCRAPING {len(urls)} URLS")
        print(f"{'='*60}")
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}]")
            result = self.scrape_post(url)
            results.append(result)
            
            # Wait between requests to avoid rate limiting
            if i < len(urls):
                wait_time = 3
                print(f"⏳ Waiting {wait_time}s before next URL...")
                time.sleep(wait_time)
        
        # Close browser
        print("\n🔒 Closing browser...")
        self.driver.quit()
        
        # Save results
        Path('output').mkdir(exist_ok=True)
        df_results = pd.DataFrame(results)
        df_results.to_excel('output/instagram_data.xlsx', index=False, engine='openpyxl')
        print(f"\n✅ Results saved to: output/instagram_data.xlsx")
        
        # Print summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        successful = sum(1 for r in results if r['status'] == 'Success')
        print(f"Total URLs processed: {len(results)}")
        print(f"Successful: {successful}/{len(results)}")
        print(f"Failed: {len(results) - successful}")
        print(f"\nTotal Likes: {sum(r['likes'] for r in results):,}")
        print(f"Total Comments: {sum(r['comments'] for r in results):,}")
        print(f"Total Views: {sum(r['views'] for r in results):,}")
        print("="*60)
        
        if successful > 0:
            print("\n✅ SUCCESS! The scraper is working!")
            print(f"📊 You can now process all 462 URLs!")
        else:
            print("\n⚠ No data was scraped.")


if __name__ == "__main__":
    scraper = InstagramSeleniumScraper()
    scraper.run()
