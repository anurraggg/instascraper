from bs4 import BeautifulSoup
import re

def analyze_html():
    try:
        with open('debug_views.html', 'r', encoding='utf-8') as f:
            html = f.read()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        print("\n--- Searching for Numbers ---")
        # Find all text nodes with numbers
        for elem in soup.find_all(string=re.compile(r'\d+')):
            text = elem.strip()
            # Filter out short numbers or dates if possible, but let's see everything first
            if len(text) < 20: 
                print(f"Text: '{text}' | Parent: {elem.parent.name} | Class: {elem.parent.get('class')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_html()
