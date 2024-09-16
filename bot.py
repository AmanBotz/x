from flask import Flask
import os
import re
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from bs4 import BeautifulSoup

# Telegram bot setup
def extract_links(page_content):
    # Parse the HTML content
    soup = BeautifulSoup(page_content, 'html.parser')
    video_pattern = r'https://xhamster.com/videos/[^"]+'
    thumbnail_pattern = r'https://ic-vt-nss.xhcdn.com/[^"]+'
    video_urls = re.findall(video_pattern, soup.text)
    thumbnail_urls = re.findall(thumbnail_pattern, soup.text)
    if len(video_urls) != len(thumbnail_urls):
        thumbnail_urls = thumbnail_urls[:len(video_urls)]
    return video_urls, thumbnail_urls

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send me a URL to extract video and thumbnail links!')

def handle_url(update: Update, context: CallbackContext) -> None:
    url = update.message.text
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

    video_urls, thumbnail_urls = extract_links(page_content)
    with open("video.txt", "w") as video_file:
        video_file.write('\n'.join(video_urls))
    with open("image.txt", "w") as image_file:
        image_file.write('\n'.join(thumbnail_urls))

    update.message.reply_document(document=open("video.txt", "rb"))
    update.message.reply_document(document=open("image.txt", "rb"))

def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_url))
    updater.start_polling()
    updater.idle()

# Flask app to avoid health check issues
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running", 200

if __name__ == '__main__':
    main()
    app.run(host='0.0.0.0', port=8000)
