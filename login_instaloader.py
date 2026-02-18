"""
Instaloader Login Helper
Run this to log in and save your session file.
"""

import instaloader
import getpass

def login():
    print("\n" + "="*60)
    print("INSTAGRAM LOGIN HELPER")
    print("="*60)
    
    L = instaloader.Instaloader()
    
    username = input("Enter Instagram Username: ").strip()
    
    try:
        print(f"Attempting login for {username}...")
        L.interactive_login(username)
        L.save_session_to_file()
        print(f"\n✅ Login successful! Session saved to: session-{username}")
        print("You can now run the scraper.")
        
    except Exception as e:
        print(f"\n✗ Login failed: {e}")
        print("Tip: If you have 2FA, try disabling it temporarily or check your phone for 'This was me' notifications.")

if __name__ == "__main__":
    login()
