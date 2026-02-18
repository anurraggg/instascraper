from bs4 import BeautifulSoup

def analyze_meta():
    try:
        with open('debug_views.html', 'r', encoding='utf-8') as f:
            html = f.read()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        meta = soup.find('meta', attrs={'name':'description'})
        if meta:
            print(f"Meta Description: {meta['content']}")
        else:
            print("Meta Description: Not Found")
            
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            print(f"OG Description: {og_desc['content']}")
        else:
            print("OG Description: Not Found")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_meta()
