#!/usr/bin/env python3
"""
Quick setup script for Real Estate Bot
"""

import os
import json

def main():
    print("🏠 Real Estate Bot - Quick Setup")
    print("=" * 40)
    
    # Your Telegram token
    telegram_token = "8465778136:AAH20TzpG2z7AyvO99-qEEpRCqZQmqWYEHw"
    
    print(f"✅ Telegram Bot Token: {telegram_token[:10]}...")
    
    # Check if credentials.json exists
    if os.path.exists('credentials.json'):
        print("✅ Found credentials.json file")
        
        # Validate the JSON file
        try:
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
                if 'type' in creds and creds['type'] == 'service_account':
                    print("✅ Google credentials file is valid")
                else:
                    print("❌ Invalid Google credentials file")
                    return
        except json.JSONDecodeError:
            print("❌ credentials.json is not valid JSON")
            return
    else:
        print("❌ credentials.json not found!")
        print("\nPlease follow these steps:")
        print("1. Go to Google Cloud Console")
        print("2. Create a project and enable Drive API")
        print("3. Create a service account")
        print("4. Download the JSON key file")
        print("5. Rename it to 'credentials.json' and place it here")
        return
    
    # Create .env file
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={telegram_token}

# Google Drive Configuration
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with your configuration")
    print("\n🎉 Setup complete! You can now run:")
    print("   python3 main.py")
    print("\nOr if python3 doesn't work, try:")
    print("   python main.py")

if __name__ == "__main__":
    main()