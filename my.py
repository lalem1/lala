from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import logging
from dotenv import load_dotenv
import os

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Define conversation states
PHOTO, DESCRIPTION, LOCATION = range(3)

# Replace with your bot token and channel ID
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN1")
CHANNEL_ID = os.getenv("CHANNEL_ID1")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a photo, and I'll ask you a few questions about it.")
    return PHOTO

# Handle photo
async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save the photo file ID
    photo_file = await update.message.photo[-1].get_file()
    context.user_data['photo_id'] = photo_file.file_id

    await update.message.reply_text("Great! Now, please describe the photo.")
    return DESCRIPTION

# Handle description
async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save the description
    context.user_data['description'] = update.message.text

    await update.message.reply_text("Thanks! Where was this photo taken?")
    return LOCATION

# Handle location
async def receive_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save the location
    context.user_data['location'] = update.message.text

    # Post to channel
    await context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=context.user_data['photo_id'],
        caption=f"Description: {context.user_data['description']}\nLocation: {context.user_data['location']}"
    )

    await update.message.reply_text("Your photo and details have been posted to the channel!")
    return ConversationHandler.END

# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

def main():
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Define conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, receive_photo)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_location)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add handlers
    application.add_handler(conv_handler)

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()