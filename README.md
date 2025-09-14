# Real Estate Telegram Bot

A Telegram bot that automatically collects real estate property data and uploads it to Google Drive.

## Features

- Interactive conversation flow for property data collection
- Automatic upload to Google Drive with organized folder structure
- Support for both Commercial and Residential properties
- Location sharing support
- Error handling and logging

## Data Collection Process

The bot collects the following information for each property:

1. **Property Type**: Commercial or Residential
2. **Address**: Full property address
3. **Area**: Property area (e.g., 1200 sq ft, 150 m²)
4. **Location**: Google Maps location or coordinates
5. **Owner Information**: Owner's name or contact number

## Setup Instructions

### 1. Prerequisites

- Python 3.7 or higher
- Telegram Bot Token (from @BotFather)
- Google Cloud Project with Drive API enabled
- Google Service Account credentials

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Telegram Bot Setup

1. Message @BotFather on Telegram
2. Create a new bot with `/newbot`
3. Follow the instructions to get your bot token
4. Add the token to your `.env` file

### 4. Google Drive Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Drive API
4. Create a Service Account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Fill in the details and create
   - Go to the service account and create a key (JSON format)
   - Download the JSON file and rename it to `credentials.json`
5. Place `credentials.json` in the project root directory

### 5. Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your configuration:
   ```
   TELEGRAM_BOT_TOKEN=your_actual_bot_token
   GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
   GOOGLE_DRIVE_FOLDER_ID=optional_folder_id
   ```

### 6. Run the Bot

```bash
python main.py
```

## Usage

1. Start a conversation with your bot on Telegram
2. Send `/start` to begin data collection
3. Follow the prompts to enter property information
4. The bot will automatically upload the data to Google Drive
5. Use `/help` for available commands
6. Use `/cancel` to stop the current operation

## File Structure

```
├── main.py                    # Main bot script
├── telegram_bot.py           # Telegram bot logic
├── google_drive_handler.py   # Google Drive integration
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── README.md                # This file
└── credentials.json         # Google service account credentials (you need to add this)
```

## Google Drive Organization

Each property entry creates:
- A new folder named: `Property_{Type}_{Timestamp}`
- A JSON file containing all the collected data
- Organized by timestamp for easy sorting

## Error Handling

The bot includes comprehensive error handling:
- Invalid input validation
- Google Drive upload errors
- Network connectivity issues
- User cancellation support

## Logging

The bot logs all activities to:
- Console output
- `bot.log` file

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- The `credentials.json` file contains sensitive information
- Consider using environment variables in production

## Troubleshooting

### Common Issues

1. **"TELEGRAM_BOT_TOKEN not found"**
   - Make sure you've created a `.env` file with your bot token

2. **"Google Drive credentials file not found"**
   - Ensure `credentials.json` is in the project root
   - Check the file path in your `.env` file

3. **"Failed to authenticate with Google Drive"**
   - Verify your service account has Drive API access
   - Check that the credentials file is valid JSON

4. **Bot not responding**
   - Check your internet connection
   - Verify the bot token is correct
   - Check the logs for error messages

### Getting Help

If you encounter issues:
1. Check the `bot.log` file for error messages
2. Verify all configuration files are set up correctly
3. Ensure all dependencies are installed
4. Test your Google Drive credentials manually

## License

This project is open source and available under the MIT License.