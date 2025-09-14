#!/usr/bin/env python3
"""
Setup guide script to help configure the Real Estate Bot
"""

import os
import json

def create_env_file():
    """Create .env file with user input"""
    print("🔧 Setting up your Real Estate Bot configuration...")
    print("\n" + "="*50)
    
    # Get Telegram Bot Token
    print("\n📱 TELEGRAM BOT SETUP:")
    print("1. Go to Telegram and search for @BotFather")
    print("2. Send /newbot and follow the instructions")
    print("3. Copy the token you receive")
    
    telegram_token = input("\nEnter your Telegram Bot Token: ").strip()
    
    if not telegram_token:
        print("❌ Telegram token is required!")
        return False
    
    # Check if credentials.json exists
    print("\n📁 GOOGLE DRIVE SETUP:")
    if os.path.exists('credentials.json'):
        print("✅ Found credentials.json file")
        credentials_file = "credentials.json"
    else:
        print("❌ credentials.json not found!")
        print("Please make sure you've downloaded the service account key from Google Cloud Console")
        print("and renamed it to 'credentials.json' in this folder.")
        return False
    
    # Optional folder ID
    print("\n📂 GOOGLE DRIVE FOLDER (Optional):")
    print("If you want to upload to a specific folder, enter the folder ID.")
    print("Otherwise, press Enter to upload to the root folder.")
    folder_id = input("Google Drive Folder ID (optional): ").strip()
    
    # Create .env file
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={telegram_token}

# Google Drive Configuration
GOOGLE_DRIVE_CREDENTIALS_FILE={credentials_file}
"""
    
    if folder_id:
        env_content += f"GOOGLE_DRIVE_FOLDER_ID={folder_id}\n"
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ Configuration saved to .env file!")
    return True

def test_credentials():
    """Test if credentials are working"""
    print("\n🧪 Testing your setup...")
    
    try:
        # Test Telegram token format
        with open('.env', 'r') as f:
            env_content = f.read()
            if 'TELEGRAM_BOT_TOKEN=' in env_content:
                print("✅ Telegram token configured")
            else:
                print("❌ Telegram token not found in .env")
                return False
        
        # Test Google credentials
        if os.path.exists('credentials.json'):
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
                if 'type' in creds and creds['type'] == 'service_account':
                    print("✅ Google credentials file is valid")
                else:
                    print("❌ Invalid Google credentials file")
                    return False
        else:
            print("❌ credentials.json not found")
            return False
        
        print("\n🎉 Setup looks good! You can now run the bot with: python main.py")
        return True
        
    except Exception as e:
        print(f"❌ Error testing setup: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🏠 Real Estate Telegram Bot Setup")
    print("="*50)
    
    if create_env_file():
        test_credentials()
    else:
        print("\n❌ Setup incomplete. Please fix the issues above and try again.")

if __name__ == "__main__":
    main()