import sys
import os
from pathlib import Path

# 方便引入 core
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from core.supabase_client import supabase
import getpass

def get_access_token():
    print("=== Supabase Access Token Generator ===")
    email = input("Enter Email: ")
    password = getpass.getpass("Enter Password: ")

    try:
        print(f"\nAttempting to login as {email}...")
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        session = res.session
        if session:
            print("\nLogin Successful!")
            print("-" * 60)
            print("Access Token:")
            print(session.access_token)
            print("-" * 60)
            print("Expires In:", session.expires_in)
            print("User ID:", res.user.id)
            
            return session.access_token
        else:
            print("\nLogin failed: No session returned.")
            
    except Exception as e:
        print(f"\nLogin failed: {str(e)}")

if __name__ == "__main__":
    get_access_token()
