import subprocess
import json

url = "https://www.instagram.com/reel/DM4_qshB3le/"
cmd = ["yt-dlp", "--dump-json", "--no-warnings", "--skip-download", url]
try:
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if result.returncode == 0:
        data = json.loads(result.stdout)
        print("Keys:", data.keys())
        print("URL:", data.get('url'))
        print("Thumbnail:", data.get('thumbnail'))
        if 'formats' in data:
            print("Formats count:", len(data['formats']))
            print("First format url:", data['formats'][0].get('url'))
    else:
        print("Error:", result.stderr)
except Exception as e:
    print("Exception:", e)
