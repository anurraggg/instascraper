import json
import time
import re
import random
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import pandas as pd
from datetime import datetime


class InstagramScraper:
    def __init__(self, config_path="config.json"):
        """Initialize the Instagram scraper with configuration."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.input_file = self.config['input_file']
        self.output_file = self.config['output_file']
        self.headless = self.config['headless']
        self.timeout = self.config['timeout']
        self.wait_time = self.config['wait_time']
        self.max_retries = self.config['max_retries']
        self.auth_file = "instagram_auth.json"
        
        # Create output directory if it doesn't exist
        Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)
    
    def load_urls(self):
        """Load Instagram URLs from CSV file."""
        try:
            df = pd.read_csv(self.input_file)
            # Get the first column (URLs)
            urls = df.iloc[:, 0].dropna().tolist()[1:]  # Skip header
            # Clean URLs
            urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
            print(f"✓ Loaded {len(urls)} URLs from {self.input_file}")
            return urls
        except Exception as e:
            print(f"✗ Error loading URLs: {e}")
            return []
    
    def extract_number(self, text):
        """Extract number from text like '1.2K', '5M', '234'."""
        if not text:
            return 0
        
        text = text.strip().upper()
        
        # Remove commas
        text = text.replace(',', '')
        
        # Handle K (thousands) and M (millions)
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
        
        # Extract number
        match = re.search(r'[\d.]+', text)
        if match:
            try:
                number = float(match.group())
                return int(number * multiplier)
            except:
                return 0
        return 0
    
    def scrape_post(self, page, url, retry_count=0):
        """Scrape data from a single Instagram post/reel."""
        try:
            print(f"\n{'='*60}")
            print(f"Scraping: {url}")
            print(f"{'='*60}")
            
            # Navigate to the URL
            page.goto(url, wait_until='networkidle', timeout=self.timeout)
            
            # Wait for initial content to load with random delay (human-like)
            initial_wait = random.uniform(3, 5)
            print(f"⏳ Waiting {initial_wait:.1f}s for page to load...")
            time.sleep(initial_wait)
            
            # Human-like scrolling pattern
            print("📜 Scrolling to load content...")
            for i in range(4):
                scroll_amount = random.randint(200, 400)
                page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                time.sleep(random.uniform(0.5, 1.5))
            
            # Scroll back up a bit (humans do this)
            page.evaluate("window.scrollBy(0, -200)")
            time.sleep(random.uniform(1, 2))
            
            data = {
                'url': url,
                'likes': 0,
                'comments': 0,
                'views': 0,
                'collaborators': '',
                'status': 'Success',
                'error': ''
            }
            
            # Use JavaScript to extract data (more reliable than selectors)
            print("🔍 Extracting data...")
            try:
                result = page.evaluate("""
                    (() => {
                        const text = document.body.innerText;
                        const likesMatch = text.match(/(\\d[\\d,\\.]*[KMB]?)\\s*likes?/i);
                        const commentsMatch = text.match(/(\\d[\\d,\\.]*[KMB]?)\\s*comments?/i) || 
                                            text.match(/View all (\\d[\\d,\\.]*[KMB]?)\\s*comments?/i);
                        const viewsMatch = text.match(/(\\d[\\d,\\.]*[KMB]?)\\s*views?/i);
                        const collabMatch = text.match(/with\\s+@?([a-zA-Z0-9._]+)/i);
                        
                        return {
                            likes: likesMatch ? likesMatch[1] : null,
                            comments: commentsMatch ? commentsMatch[1] : null,
                            views: viewsMatch ? viewsMatch[1] : null,
                            collaborator: collabMatch ? collabMatch[1] : null,
                            hasLoginPrompt: text.toLowerCase().includes('log in') && text.toLowerCase().includes('sign up')
                        };
                    })()
                """)
                
                # Process the results
                if result['likes']:
                    data['likes'] = self.extract_number(result['likes'])
                    print(f"✓ Likes: {data['likes']:,}")
                
                if result['comments']:
                    data['comments'] = self.extract_number(result['comments'])
                    print(f"✓ Comments: {data['comments']:,}")
                
                if result['views']:
                    data['views'] = self.extract_number(result['views'])
                    print(f"✓ Views: {data['views']:,}")
                
                if result['collaborator']:
                    data['collaborators'] = result['collaborator']
                    print(f"✓ Collaborators: {data['collaborators']}")
                
                # Check if login is required
                if result['hasLoginPrompt'] and data['likes'] == 0:
                    data['status'] = 'Login Required'
                    data['error'] = 'Instagram requires login to view this content'
                    print(f"⚠ Login required for this post")
                elif data['likes'] == 0 and data['comments'] == 0 and data['views'] == 0:
                    # Take a screenshot for debugging
                    screenshot_path = f"output/debug_{url.split('/')[-2]}.png"
                    try:
                        page.screenshot(path=screenshot_path)
                        print(f"📸 Screenshot saved to {screenshot_path}")
                    except:
                        pass
                    
                    data['status'] = 'No Data'
                    data['error'] = 'Could not extract any metrics'
                    print(f"⚠ No data could be extracted")
                
            except Exception as e:
                print(f"⚠ JavaScript extraction failed: {e}")
                # Fallback to text-based extraction
                page_text = page.inner_text('body')
                
                # Try regex patterns on page text
                likes_match = re.search(r'([\d,\.]+[KMB]?)\s*likes?', page_text, re.IGNORECASE)
                if likes_match:
                    data['likes'] = self.extract_number(likes_match.group(1))
                    print(f"✓ Likes (fallback): {data['likes']:,}")
            
            return data
            
        except PlaywrightTimeout:
            if retry_count < self.max_retries:
                print(f"⚠ Timeout, retrying... ({retry_count + 1}/{self.max_retries})")
                time.sleep(random.uniform(3, 5))
                return self.scrape_post(page, url, retry_count + 1)
            else:
                print(f"✗ Timeout after {self.max_retries} retries")
                return {
                    'url': url,
                    'likes': 0,
                    'comments': 0,
                    'views': 0,
                    'collaborators': '',
                    'status': 'Timeout',
                    'error': 'Page took too long to load'
                }
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return {
                'url': url,
                'likes': 0,
                'comments': 0,
                'views': 0,
                'collaborators': '',
                'status': 'Error',
                'error': str(e)
            }
    
    def manual_login(self, context, page):
        """Allow user to manually log in to Instagram and save auth state."""
        print("\n" + "="*60)
        print("MANUAL LOGIN")
        print("="*60)
        print("\n📱 Opening Instagram login page...")
        print("👉 Please log in to your Instagram account in the browser")
        print("👉 After logging in, press ENTER here to continue...")
        print("👉 Your session will be saved for future runs!\n")
        
        # Navigate to Instagram
        page.goto("https://www.instagram.com/", wait_until='domcontentloaded')
        time.sleep(5)
        
        # Wait for user to log in
        input("Press ENTER after you have logged in to Instagram: ")
        
        # Verify login by checking if we're still on login page
        current_url = page.url
        page_text = page.inner_text('body').lower()
        
        if "log in" in page_text and "sign up" in page_text and len(page_text) < 5000:
            print("\n⚠️  It looks like you might not be logged in yet.")
            retry = input("Do you want to try again? (y/n): ")
            if retry.lower() == 'y':
                return self.manual_login(context, page)
        
        # Save authentication state
        try:
            context.storage_state(path=self.auth_file)
            print(f"\n✅ Login successful! Session saved to {self.auth_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save session: {e}")
        
        print("✅ Starting scraping...\n")
        time.sleep(2)
    
    def run(self):
        """Run the scraper on all URLs."""
        print("\n" + "="*60)
        print("INSTAGRAM SCRAPER")
        print("="*60)
        
        urls = self.load_urls()
        if not urls:
            print("✗ No URLs to scrape!")
            return
        
        results = []
        
        with sync_playwright() as p:
            print(f"\n🚀 Launching browser (headless={self.headless})...")
            browser = p.chromium.launch(headless=self.headless)
            
            # Check if we have saved authentication
            auth_exists = Path(self.auth_file).exists()
            
            if auth_exists:
                print(f"✓ Found saved session: {self.auth_file}")
                context = browser.new_context(
                    storage_state=self.auth_file,
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
            else:
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
            
            page = context.new_page()
            
            # Manual login step if no saved auth or if user wants to re-login
            if not auth_exists:
                self.manual_login(context, page)
            else:
                print("✓ Using saved login session\n")
            
            # Process each URL
            for i, url in enumerate(urls, 1):
                print(f"\n[{i}/{len(urls)}] Processing...")
                data = self.scrape_post(page, url)
                results.append(data)
                
                # Longer idle time between requests to avoid detection (5-10 seconds)
                if i < len(urls):
                    idle_time = random.uniform(5, 10)
                    print(f"\n💤 Idle time: {idle_time:.1f}s (avoiding detection)...")
                    time.sleep(idle_time)
            
            browser.close()
        
        # Save results to Excel
        self.save_results(results)
        
        # Print summary
        self.print_summary(results)
    
    def save_results(self, results):
        """Save results to Excel file."""
        try:
            df = pd.DataFrame(results)
            df.to_excel(self.output_file, index=False, engine='openpyxl')
            print(f"\n✓ Results saved to: {self.output_file}")
        except Exception as e:
            print(f"\n✗ Error saving results: {e}")
    
    def print_summary(self, results):
        """Print summary statistics."""
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        total = len(results)
        success = sum(1 for r in results if r['status'] == 'Success')
        failed = total - success
        
        total_likes = sum(r['likes'] for r in results)
        total_comments = sum(r['comments'] for r in results)
        total_views = sum(r['views'] for r in results)
        
        print(f"Total URLs processed: {total}")
        print(f"Successful: {success}")
        print(f"Failed: {failed}")
        print(f"\nTotal Likes: {total_likes:,}")
        print(f"Total Comments: {total_comments:,}")
        print(f"Total Views: {total_views:,}")
        print("="*60)


if __name__ == "__main__":
    scraper = InstagramScraper()
    scraper.run()
