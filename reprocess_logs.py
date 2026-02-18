import glob
import re
import json
import os
from pathlib import Path

def extract_number(text):
    """Extract number from text."""
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

def parse_log_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Split header and content
    parts = content.split('--- TEXT CONTENT ---')
    if len(parts) < 2:
        return None
        
    header = parts[0]
    body = parts[1]
    
    # Extract URL
    url = ''
    url_match = re.search(r'URL: (https?://[^\s]+)', header)
    if url_match:
        url = url_match.group(1)
        
    # Parse Metrics
    likes = 0
    comments = 0
    views = 0
    collaborators = ''
    
    # Likes
    likes_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*likes', body, re.I)
    if not likes_match:
        likes_match = re.search(r'and\s+(\d[\d,\.]*[KMB]?)\s+others', body, re.I)
    if not likes_match:
        likes_match = re.search(r'Liked by\s+[^\n]+\s+and\s+(\d[\d,\.]*[KMB]?)', body, re.I)
    if likes_match:
        likes = extract_number(likes_match.group(1))
        
    # Comments
    comments_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*comments', body, re.I)
    if not comments_match:
        comments_match = re.search(r'View all (\d[\d,\.]*[KMB]?)\s*comments', body, re.I)
    if comments_match:
        comments = extract_number(comments_match.group(1))
        
    # Views (from text or aria labels)
    views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*views', body, re.I)
    if not views_match:
        views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*plays', body, re.I)
    if views_match:
        views = extract_number(views_match.group(1))
        
    # Collaborators
    collab_match = re.search(r'with\s+@?([a-zA-Z0-9._]+)', body, re.I)
    if not collab_match:
            collab_match = re.search(r'and\s+@?([a-zA-Z0-9._]+)', body, re.I)
    if collab_match:
        collaborators = collab_match.group(1)
        
    # Fallback for Reels (Line based)
    if likes == 0 and comments == 0:
        lines = body.split('\n')
        for idx, line in enumerate(lines):
            line = line.strip()
            if line.lower() == 'likes' and idx + 1 < len(lines):
                next_line = lines[idx+1].strip()
                if re.match(r'^[\d,\.]+[KMB]?$', next_line):
                    likes = extract_number(next_line)
                    break
            if '… more' in line and idx + 1 < len(lines):
                next_line = lines[idx+1].strip()
                if re.match(r'^[\d,\.]+[KMB]?$', next_line):
                    likes = extract_number(next_line)
                    if idx + 2 < len(lines):
                        next_next_line = lines[idx+2].strip()
                        if re.match(r'^[\d,\.]+[KMB]?$', next_next_line):
                            comments = extract_number(next_next_line)
                    break

    status = 'Success' if (likes > 0 or comments > 0 or views > 0) else 'No Data'
    
    return {
        'url': url,
        'likes': likes,
        'comments': comments,
        'views': views,
        'followers': 0, # Can't easily extract from body unless we look for it specifically
        'following': 0,
        'collaborators': collaborators,
        'status': status,
        'error': ''
    }

def main():
    print("Reprocessing logs...")
    log_files = glob.glob("logs/url_*.txt")
    print(f"Found {len(log_files)} text logs.")
    
    count = 0
    for log_file in log_files:
        try:
            result = parse_log_file(log_file)
            if result:
                # Save as result.json
                base_name = os.path.splitext(log_file)[0]
                json_path = f"{base_name}_result.json"
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)
                count += 1
        except Exception as e:
            print(f"Error processing {log_file}: {e}")
            
    print(f"✅ Created {count} result.json files.")

if __name__ == "__main__":
    main()
