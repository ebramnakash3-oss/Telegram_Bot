#!/usr/bin/env python3
"""
Real Estate Telegram Bot
Automatically collects property data and uploads to Google Drive
"""

import os
import sys
import logging
from telegram_bot import RealEstateBot
from config import TELEGRAM_BOT_TOKEN, GOOGLE_DRIVE_CREDENTIALS_FILE

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_requirements():
    """Check if all required files and configurations are present."""
    errors = []
    
    # Check Telegram bot token
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN not found in environment variables")
    
    # Check Google Drive credentials file
    if not os.path.exists(GOOGLE_DRIVE_CREDENTIALS_FILE):
        errors.append(f"Google Drive credentials file not found: {GOOGLE_DRIVE_CREDENTIALS_FILE}")
    
    if errors:
        logger.error("Configuration errors found:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
    
    return True

def main():
    """Main function to run the bot."""
    logger.info("Starting Real Estate Telegram Bot...")
    
    # Check requirements
    if not check_requirements():
        logger.error("Please fix the configuration errors before running the bot.")
        sys.exit(1)
    
    try:
        # Initialize bot
        bot = RealEstateBot()
        
        # Create application
        from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, filters
        
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Add conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', bot.start)],
            states={
                bot.PROPERTY_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.property_type)],
                bot.ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.address)],
                bot.AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.area)],
                bot.LOCATION: [MessageHandler(filters.TEXT | filters.LOCATION, bot.location)],
                bot.OWNER_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.owner_info)],
            },
            fallbacks=[CommandHandler('cancel', bot.cancel)],
        )
        
        app.add_handler(conv_handler)
        app.add_handler(CommandHandler('help', bot.help_command))
        app.add_error_handler(bot.error_handler)
        
        # Start the bot
        logger.info("Bot is running... Press Ctrl+C to stop.")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()