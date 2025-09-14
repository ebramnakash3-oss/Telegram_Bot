import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    ConversationHandler, filters, ContextTypes
)
from google_drive_handler import GoogleDriveHandler
from config import TELEGRAM_BOT_TOKEN, GOOGLE_DRIVE_CREDENTIALS_FILE, PROPERTY_TYPES

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
PROPERTY_TYPE, ADDRESS, AREA, LOCATION, OWNER_INFO = range(5)

class RealEstateBot:
    def __init__(self):
        self.drive_handler = GoogleDriveHandler(GOOGLE_DRIVE_CREDENTIALS_FILE)
        self.user_data = {}
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the conversation and ask for property type."""
        user = update.effective_user
        self.user_data[user.id] = {}
        
        keyboard = [PROPERTY_TYPES]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        
        await update.message.reply_text(
            f"Hello {user.first_name}! 🏠\n\n"
            "I'll help you collect real estate data and upload it to Google Drive.\n\n"
            "Let's start with the property type:",
            reply_markup=reply_markup
        )
        
        return PROPERTY_TYPE
    
    async def property_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store property type and ask for address."""
        user = update.effective_user
        property_type = update.message.text
        
        if property_type not in PROPERTY_TYPES:
            await update.message.reply_text(
                "Please select a valid property type from the options above:",
                reply_markup=ReplyKeyboardMarkup([PROPERTY_TYPES], one_time_keyboard=True)
            )
            return PROPERTY_TYPE
        
        self.user_data[user.id]['property_type'] = property_type
        
        await update.message.reply_text(
            f"Great! Property type: {property_type}\n\n"
            "Now, please provide the property address:",
            reply_markup=ReplyKeyboardRemove()
        )
        
        return ADDRESS
    
    async def address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store address and ask for area."""
        user = update.effective_user
        address = update.message.text
        
        if not address.strip():
            await update.message.reply_text("Please provide a valid address:")
            return ADDRESS
        
        self.user_data[user.id]['address'] = address.strip()
        
        await update.message.reply_text(
            f"Address recorded: {address}\n\n"
            "What is the area of the property? (e.g., 1200 sq ft, 150 m²):"
        )
        
        return AREA
    
    async def area(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store area and ask for Google Maps location."""
        user = update.effective_user
        area = update.message.text
        
        if not area.strip():
            await update.message.reply_text("Please provide the property area:")
            return AREA
        
        self.user_data[user.id]['area'] = area.strip()
        
        await update.message.reply_text(
            f"Area recorded: {area}\n\n"
            "Please provide the Google Maps location or coordinates:\n"
            "(You can share a location, paste a Google Maps link, or type coordinates)"
        )
        
        return LOCATION
    
    async def location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store location and ask for owner information."""
        user = update.effective_user
        
        # Handle location message (could be text, location, or document)
        if update.message.location:
            location_data = f"Lat: {update.message.location.latitude}, Lon: {update.message.location.longitude}"
        else:
            location_data = update.message.text
        
        if not location_data.strip():
            await update.message.reply_text("Please provide the location information:")
            return LOCATION
        
        self.user_data[user.id]['location'] = location_data.strip()
        
        await update.message.reply_text(
            f"Location recorded: {location_data}\n\n"
            "Finally, please provide the owner's name or contact number:"
        )
        
        return OWNER_INFO
    
    async def owner_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store owner information and upload to Google Drive."""
        user = update.effective_user
        owner_info = update.message.text
        
        if not owner_info.strip():
            await update.message.reply_text("Please provide the owner's information:")
            return OWNER_INFO
        
        self.user_data[user.id]['owner_info'] = owner_info.strip()
        
        # Show summary
        property_data = self.user_data[user.id]
        summary = (
            f"📋 **Property Data Summary:**\n\n"
            f"🏠 **Type:** {property_data['property_type']}\n"
            f"📍 **Address:** {property_data['address']}\n"
            f"📏 **Area:** {property_data['area']}\n"
            f"🗺️ **Location:** {property_data['location']}\n"
            f"👤 **Owner:** {property_data['owner_info']}\n\n"
            "Uploading to Google Drive..."
        )
        
        await update.message.reply_text(summary, parse_mode='Markdown')
        
        try:
            # Upload to Google Drive
            folder_id = self.drive_handler.upload_property_data(property_data, str(user.id))
            
            await update.message.reply_text(
                f"✅ **Success!**\n\n"
                f"Your property data has been uploaded to Google Drive!\n"
                f"Folder ID: `{folder_id}`\n\n"
                f"Type /start to add another property or /help for more options.",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error uploading to Google Drive: {str(e)}")
            await update.message.reply_text(
                f"❌ **Error uploading to Google Drive:**\n"
                f"`{str(e)}`\n\n"
                f"Please try again or contact support.",
                parse_mode='Markdown'
            )
        
        # Clear user data
        if user.id in self.user_data:
            del self.user_data[user.id]
        
        return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the conversation."""
        user = update.effective_user
        
        if user.id in self.user_data:
            del self.user_data[user.id]
        
        await update.message.reply_text(
            "Operation cancelled. Type /start to begin again.",
            reply_markup=ReplyKeyboardRemove()
        )
        
        return ConversationHandler.END
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send help message."""
        help_text = (
            "🏠 **Real Estate Data Bot**\n\n"
            "**Commands:**\n"
            "/start - Begin collecting property data\n"
            "/help - Show this help message\n"
            "/cancel - Cancel current operation\n\n"
            "**Data Collection Process:**\n"
            "1. Property Type (Commercial/Residential)\n"
            "2. Property Address\n"
            "3. Property Area\n"
            "4. Google Maps Location\n"
            "5. Owner Information\n\n"
            "All data is automatically uploaded to Google Drive!"
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log errors."""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "An error occurred. Please try again or contact support."
            )