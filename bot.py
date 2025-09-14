import logging
import os
from dataclasses import dataclass, asdict
from typing import Dict

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from drive_client import DriveClient

# Load environment
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GDRIVE_PARENT_FOLDER_ID = os.getenv("GDRIVE_PARENT_FOLDER_ID", "")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
OAUTH_CLIENT_SECRETS = os.getenv("GOOGLE_OAUTH_CLIENT_SECRETS")
OAUTH_TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
if not GDRIVE_PARENT_FOLDER_ID:
    raise RuntimeError("GDRIVE_PARENT_FOLDER_ID is not set")

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("realestate_bot")

# Conversation states
(PROPERTY_TYPE, ADDRESS, AREA, MAP_LOCATION, OWNER) = range(5)

PROPERTY_KEYBOARD = ReplyKeyboardMarkup(
    [["Residential"], ["Commercial"]], one_time_keyboard=True, resize_keyboard=True
)


@dataclass
class PropertyEntry:
    property_type: str
    address: str
    area: str
    maps_location: str
    owner: str

    def to_folder_name(self) -> str:
        safe_address = self.address.strip().replace("/", "-")
        safe_type = self.property_type.strip()
        return f"{safe_type} - {safe_address}"


def build_drive_client() -> DriveClient:
    return DriveClient(
        parent_folder_id=GDRIVE_PARENT_FOLDER_ID,
        service_account_file=SERVICE_ACCOUNT_FILE,
        oauth_client_secrets=OAUTH_CLIENT_SECRETS,
        oauth_token_file=OAUTH_TOKEN_FILE,
    )


entries_by_user: Dict[int, PropertyEntry] = {}

drive_client = build_drive_client()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Welcome! Let's capture a new property entry.\n\n"
        "First, choose the property type:",
        reply_markup=PROPERTY_KEYBOARD,
    )
    return PROPERTY_TYPE


async def property_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text.lower() not in {"residential", "commercial"}:
        await update.message.reply_text("Please choose: Residential or Commercial.", reply_markup=PROPERTY_KEYBOARD)
        return PROPERTY_TYPE

    user_id = update.effective_user.id
    entries_by_user[user_id] = PropertyEntry(property_type=text.title(), address="", area="", maps_location="", owner="")

    await update.message.reply_text("Please enter the property address:", reply_markup=ReplyKeyboardRemove())
    return ADDRESS


async def address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    user_id = update.effective_user.id
    entry = entries_by_user.get(user_id)
    if not entry:
        await update.message.reply_text("Let's start again. Send /start")
        return ConversationHandler.END
    entry.address = text

    await update.message.reply_text("Enter the area (e.g., 120 sqm):")
    return AREA


async def area(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    user_id = update.effective_user.id
    entry = entries_by_user.get(user_id)
    if not entry:
        await update.message.reply_text("Let's start again. Send /start")
        return ConversationHandler.END
    entry.area = text

    await update.message.reply_text("Paste the Google Maps location link:")
    return MAP_LOCATION


async def map_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    user_id = update.effective_user.id
    entry = entries_by_user.get(user_id)
    if not entry:
        await update.message.reply_text("Let's start again. Send /start")
        return ConversationHandler.END
    entry.maps_location = text

    await update.message.reply_text("Owner name or phone number:")
    return OWNER


async def owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    user_id = update.effective_user.id
    entry = entries_by_user.get(user_id)
    if not entry:
        await update.message.reply_text("Let's start again. Send /start")
        return ConversationHandler.END
    entry.owner = text

    try:
        folder_name = entry.to_folder_name()
        folder_id = drive_client.ensure_folder(folder_name)
        drive_client.upload_json("data.json", asdict(entry), parent_id=folder_id)
        await update.message.reply_text(
            "Saved successfully to Google Drive. Send /start to add another.",
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception as e:
        logger.exception("Upload failed")
        await update.message.reply_text(f"Failed to save to Google Drive: {e}")

    entries_by_user.pop(user_id, None)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    entries_by_user.pop(update.effective_user.id, None)
    await update.message.reply_text("Cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PROPERTY_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, property_type)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
            AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, area)],
            MAP_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, map_location)],
            OWNER: [MessageHandler(filters.TEXT & ~filters.COMMAND, owner)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv)

    # run_polling blocks and manages the async event loop internally
    application.run_polling()


if __name__ == "__main__":
    main()