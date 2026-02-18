# Instagram Scraper

A robust Instagram scraper that extracts likes, comments, views, and collaborators from Instagram posts and reels.

## Features

✅ Scrapes **likes**, **comments**, **views**, and **collaborators**  
✅ Supports both **posts** and **reels**  
✅ Handles multiple URL formats  
✅ Automatic retry on failures  
✅ Exports results to **Excel**  
✅ Detailed progress tracking  

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

```bash
playwright install chromium
```

## Usage

### Basic Usage

Simply run the scraper:

```bash
python scraper.py
```

The scraper will:
1. Read URLs from `input/Instagram_URLS.csv`
2. Scrape each URL
3. Save results to `output/instagram_data.xlsx`

### Configuration

Edit `config.json` to customize settings:

```json
{
  "input_file": "input/Instagram_URLS.csv",
  "output_file": "output/instagram_data.xlsx",
  "headless": false,              // Set to true to hide browser
  "timeout": 30000,                // Page load timeout (ms)
  "wait_time": 3000,               // Wait time after page load (ms)
  "max_retries": 3                 // Number of retries on failure
}
```

## Input Format

Your CSV file should have URLs in the first column:

```
INSTAGRAM URLS
https://www.instagram.com/reel/ABC123/
https://www.instagram.com/p/DEF456/
```

## Output Format

The Excel file will contain:

| Column | Description |
|--------|-------------|
| url | Instagram URL |
| likes | Number of likes |
| comments | Number of comments |
| views | Number of views (for reels/videos) |
| collaborators | Collaborator names (if any) |
| status | Success/Error/Login Required |
| error | Error message (if any) |

## Troubleshooting

### "Login Required" Error

Instagram may require login for some content. Solutions:
1. Run with `headless: false` and manually log in when prompted
2. The browser will stay open - log in once and the session will persist

### No Data Extracted

If the scraper returns zeros:
- Instagram's layout may have changed
- The post might be private
- Try running with `headless: false` to see what's happening

### Slow Performance

- Increase `wait_time` in config.json (e.g., 5000ms)
- Check your internet connection
- Instagram may be rate-limiting you

## Tips

🔹 **First Run**: Set `headless: false` to see the browser and verify it's working  
🔹 **Login**: If prompted, log in manually - the session will persist  
🔹 **Rate Limiting**: Add delays between requests (already built-in)  
🔹 **Large Lists**: Process in batches to avoid detection  

## Example Output

```
============================================================
INSTAGRAM SCRAPER
============================================================

✓ Loaded 10 URLs from input/Instagram_URLS.csv

🚀 Launching browser (headless=False)...

[1/10] Processing...
============================================================
Scraping: https://www.instagram.com/reel/ABC123/
============================================================
✓ Likes: 15234 (from: 15K)
✓ Comments: 892 (from: 892)
✓ Views: 125000 (from: 125K)

✓ Results saved to: output/instagram_data.xlsx

============================================================
SUMMARY
============================================================
Total URLs processed: 10
Successful: 9
Failed: 1

Total Likes: 45,678
Total Comments: 3,456
Total Views: 567,890
============================================================
```

## Notes

⚠️ **Use Responsibly**: Respect Instagram's Terms of Service  
⚠️ **Rate Limiting**: Don't scrape too aggressively  
⚠️ **Privacy**: Only scrape public content  

---

**Need help?** Check the error messages in the Excel output for specific issues.
