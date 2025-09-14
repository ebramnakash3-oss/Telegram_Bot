#!/usr/bin/env python3
"""
Check if credentials.json file exists and is valid
"""

import os
import json

def check_credentials():
    print("🔍 Checking for credentials.json file...")
    print("=" * 50)
    
    # Check if file exists
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json file not found!")
        print("\n📋 To add the file:")
        print("1. Download the JSON file from Google Cloud Console")
        print("2. Place it in this folder: /workspace")
        print("3. Rename it to exactly: credentials.json")
        print("\n💡 You can:")
        print("   - Drag and drop the file into this folder")
        print("   - Use file upload in your editor")
        print("   - Copy the file using terminal commands")
        return False
    
    print("✅ credentials.json file found!")
    
    # Check if it's valid JSON
    try:
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
            
        # Check if it has the required fields
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds]
        
        if missing_fields:
            print(f"❌ Invalid credentials file. Missing fields: {missing_fields}")
            return False
        
        if creds.get('type') != 'service_account':
            print("❌ Invalid credentials file. Type should be 'service_account'")
            return False
        
        print("✅ credentials.json file is valid!")
        print(f"📧 Service account email: {creds.get('client_email', 'Unknown')}")
        print(f"🆔 Project ID: {creds.get('project_id', 'Unknown')}")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ credentials.json is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials file: {str(e)}")
        return False

def main():
    if check_credentials():
        print("\n🎉 Your setup is complete!")
        print("You can now run your bot with:")
        print("   source venv/bin/activate")
        print("   python3 main.py")
    else:
        print("\n❌ Please add the credentials.json file first")

if __name__ == "__main__":
    main()