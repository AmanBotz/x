import os
import re
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from bs4 import BeautifulSoup

# Function to extract video and thumbnail links
def extract_links(page_content):
    # Parse the HTML content
    soup = BeautifulSoup(page_content, 'html.parser')
    
    # Regex for matching video and thumbnail URLs
    video_pattern = r'https://xhamster.com/videos/[^"]+'
    thumbnail_pattern = r'https://ic-vt-nss.xhcdn.com/[^"]+'
    
    # Extracting video and thumbnail URLs
    video_urls = re.findall(video_pattern, soup.text)
    thumbnail_urls = re.findall(thumbnail_pattern, soup.text)
    
    # Ensure the lists are of equal length
    if len(video_urls) != len(thumbnail_urls):
        thumbnail_urls = thumbnail_urls[:len(video_urls)]
    
    return video_urls, thumbnail_urls

# Command to start the bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send me a URL to extract video and thumbnail links!')

# URL handler
def handle_url(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    
    # Fetch the page content
    try:
        response = requests.get(url)
        if response.status_code == 200:
            page_content = response.text
        else:
            update.message.reply_text(f"Error fetching the URL: {response.status_code}")
            return
    except Exception as e:
        update.message.reply_text(f"Error: {e}")
        return
    
    # Extract the links
    video_urls, thumbnail_urls = extract_links(page_content)
    
    # Save to files
    with open("video.txt", "w") as video_file:
        video_file.write('\n'.join(video_urls))
        
    with open("image.txt", "w") as image_file:
        image_file.write('\n'.join(thumbnail_urls))
    
    # Send the files back to the user
    update.message.reply_document(document=open("video.txt", "rb"))
    update.message.reply_document(document=open("image.txt", "rb"))

def main():
    # Your Telegram API token
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Start command
    dispatcher.add_handler(CommandHandler("start", start))
    
    # URL handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_url))
    
    # Start the bot
    updater.start_polling()
    
    # Run until you press Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
