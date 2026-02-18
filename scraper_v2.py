import json
import time
import re
import random
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import pandas as pd
from datetime import datetime


class InstagramScraperV2:
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
        self.api_data = {}
        
        # Create output directory if it doesn't exist
        Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)
    
    def load_urls(self):
        """Load Instagram URLs from CSV file."""
        try:
            df = pd.read_csv(self.input_file)
            urls = df.iloc[:, 0].dropna().tolist()[1:]
            urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
            print(f"✓ Loaded {len(urls)} URLs from {self.input_file}")
            return urls
        except Exception as e:
            print(f"✗ Error loading URLs: {e}")
            return []
    
    def extract_number(self, text):
        """Extract number from text like '1.2K', '5M', '234'."""
        if not text or text == 'null':
            return 0
        
        text = str(text).strip().upper()
        text = text.replace(',', '')
        
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
                number = float(match.group())
                return int(number * multiplier)
            except:
                return 0
        return 0
    
    def intercept_api_response(self, response):
        """Intercept API responses to capture Instagram data."""
        try:
            url = response.url
            if 'graphql/query' in url or '/api/v1/' in url:
                try:
                    json_data = response.json()
                    self.api_data[url] = json_data
                except:
                    pass
        except:
            pass
    
    def scrape_post(self, page, url, retry_count=0):
        """Scrape data from a single Instagram post/reel."""
        try:
            print(f"\n{'='*60}")
            print(f"Scraping: {url}")
            print(f"{'='*60}")
            
            # Clear previous API data
            self.api_data = {}
            
            # Set up response interception
            page.on("response", self.intercept_api_response)
            
            # Navigate to the URL
            page.goto(url, wait_until='networkidle', timeout=self.timeout)
            
            # Wait and scroll
            initial_wait = random.uniform(4, 6)
            print(f"⏳ Waiting {initial_wait:.1f}s for page to load...")
            time.sleep(initial_wait)
            
            print("📜 Scrolling to load content...")
            for i in range(3):
                scroll_amount = random.randint(300, 500)
                page.evaluate(f"window.scrollBy(0, {scroll_amount})")
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
            
            # Try to extract from API responses first
            print("🔍 Checking intercepted API data...")
            for api_url, api_response in self.api_data.items():
                try:
                    # Look for metrics in the API response
                    json_str = json.dumps(api_response)
                    
                    # Search for like count
                    like_patterns = [
                        r'"like_count":(\d+)',
                        r'"edge_media_preview_like":\{"count":(\d+)\}',
                        r'"edge_liked_by":\{"count":(\d+)\}'
                    ]
                    for pattern in like_patterns:
                        match = re.search(pattern, json_str)
                        if match:
                            likes = int(match.group(1))
                            if likes > data['likes']:
                                data['likes'] = likes
                    
                    # Search for comment count
                    comment_patterns = [
                        r'"comment_count":(\d+)',
                        r'"edge_media_to_comment":\{"count":(\d+)\}',
                        r'"edge_media_preview_comment":\{"count":(\d+)\}'
                    ]
                    for pattern in comment_patterns:
                        match = re.search(pattern, json_str)
                        if match:
                            comments = int(match.group(1))
                            if comments > data['comments']:
                                data['comments'] = comments
                    
                    # Search for view count
                    view_patterns = [
                        r'"video_view_count":(\d+)',
                        r'"view_count":(\d+)',
                        r'"play_count":(\d+)'
                    ]
                    for pattern in view_patterns:
                        match = re.search(pattern, json_str)
                        if match:
                            views = int(match.group(1))
                            if views > data['views']:
                                data['views'] = views
                except:
                    continue
            
            if data['likes'] > 0:
                print(f"✓ Likes (from API): {data['likes']:,}")
            if data['comments'] > 0:
                print(f"✓ Comments (from API): {data['comments']:,}")
            if data['views'] > 0:
                print(f"✓ Views (from API): {data['views']:,}")
            
            # If API didn't work, try DOM extraction
            if data['likes'] == 0:
                print("🔍 Trying DOM extraction...")
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
                                collaborator: collabMatch ? collabMatch[1] : null
                            };
                        })()
                    """)
                    
                    if result['likes']:
                        data['likes'] = self.extract_number(result['likes'])
                        print(f"✓ Likes (from DOM): {data['likes']:,}")
                    
                    if result['comments']:
                        data['comments'] = self.extract_number(result['comments'])
                        print(f"✓ Comments (from DOM): {data['comments']:,}")
                    
                    if result['views']:
                        data['views'] = self.extract_number(result['views'])
                        print(f"✓ Views (from DOM): {data['views']:,}")
                    
                    if result['collaborator']:
                        data['collaborators'] = result['collaborator']
                        print(f"✓ Collaborators: {data['collaborators']}")
                        
                except Exception as e:
                    print(f"⚠ DOM extraction failed: {e}")
            
            # Check if we got any data
            if data['likes'] == 0 and data['comments'] == 0 and data['views'] == 0:
                screenshot_path = f"output/debug_{url.split('/')[-2]}.png"
                try:
                    page.screenshot(path=screenshot_path)
                    print(f"📸 Screenshot saved to {screenshot_path}")
                except:
                    pass
                
                data['status'] = 'No Data'
                data['error'] = 'Could not extract any metrics'
                print(f"⚠ No data could be extracted")
            
            return data
            
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
        
        page.goto("https://www.instagram.com/", wait_until='domcontentloaded')
        time.sleep(5)
        
        input("Press ENTER after you have logged in to Instagram: ")
        
        current_url = page.url
        page_text = page.inner_text('body').lower()
        
        if "log in" in page_text and "sign up" in page_text and len(page_text) < 5000:
            print("\n⚠️  It looks like you might not be logged in yet.")
            retry = input("Do you want to try again? (y/n): ")
            if retry.lower() == 'y':
                return self.manual_login(context, page)
        
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
        print("INSTAGRAM SCRAPER V2 (API Interception)")
        print("="*60)
        
        urls = self.load_urls()
        if not urls:
            print("✗ No URLs to scrape!")
            return
        
        results = []
        
        with sync_playwright() as p:
            print(f"\n🚀 Launching browser (headless={self.headless})...")
            browser = p.chromium.launch(headless=self.headless)
            
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
            
            if not auth_exists:
                self.manual_login(context, page)
            else:
                print("✓ Using saved login session\n")
            
            # Process each URL
            for i, url in enumerate(urls, 1):
                print(f"\n[{i}/{len(urls)}] Processing...")
                data = self.scrape_post(page, url)
                results.append(data)
                
                if i < len(urls):
                    idle_time = random.uniform(5, 10)
                    print(f"\n💤 Idle time: {idle_time:.1f}s (avoiding detection)...")
                    time.sleep(idle_time)
            
            browser.close()
        
        # Save results
        self.save_results(results)
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
    scraper = InstagramScraperV2()
    scraper.run()
