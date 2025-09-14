#!/usr/bin/env python3
"""
Create .env file with the Telegram bot token
"""

def main():
    # Your Telegram bot token
    telegram_token = "8465778136:AAH20TzpG2z7AyvO99-qEEpRCqZQmqWYEHw"
    
    # Create .env file
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={telegram_token}

# Google Drive Configuration
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with your Telegram bot token!")
    print("📁 Now you need to add your Google Drive credentials file:")
    print("   1. Go to Google Cloud Console")
    print("   2. Create a project and enable Drive API")
    print("   3. Create a service account")
    print("   4. Download the JSON key file")
    print("   5. Rename it to 'credentials.json' and place it in this folder")
    print("\nOnce you have credentials.json, run: python3 main.py")

if __name__ == "__main__":
    main()