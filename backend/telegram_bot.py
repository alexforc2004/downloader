import logging
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from downloader import downloader

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN", "8282348584:AAEu9K_-rwSI3Sh1obae64iqE9MtaicnbcQ")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit for Telegram bots


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to **alexDownloader Bot**!\n\n"
        "Send me any URL from YouTube, Instagram, or TikTok and I'll send you the file with full picture and audio! 🎮✨\n\n"
        "Commands:\n"
        "/download [url] - Download as video\n"
        "/audio [url] - Download as mp3"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith(('http://', 'https://')):
        return

    await process_download(update, context, url, "video")

async def download_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a URL. Example: /download https://...")
        return
    await process_download(update, context, context.args[0], "video")

async def audio_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a URL. Example: /audio https://...")
        return
    await process_download(update, context, context.args[0], "audio")

async def process_download(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, format_type: str):
    status_msg = await update.message.reply_text(f"🚀 Processing your {format_type}... Please wait.")
    
    try:
        # Get info first
        info = downloader.get_info(url)
        await status_msg.edit_text(f"📦 Found: **{info['title']}**\nDownloading now...")
        
        # Download with 50MB limit (Telegram's restriction)
        result = downloader.download_media(url, format_type, max_filesize_mb=50)
        file_path = result['path']
        title = result['title']
        
        await status_msg.edit_text("📤 Sending file to you...")
        
        # Check file size before sending
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            size_mb = round(file_size / (1024 * 1024), 2)
            await status_msg.edit_text(
                f"⚠️ **File is too large ({size_mb}MB)**\n\n"
                f"Telegram bots are limited to **50MB** for uploads. "
                f"Please try a shorter video or a lower quality format."
            )
            if os.path.exists(file_path):
                os.remove(file_path)
            return

        if format_type == "audio":
            await update.message.reply_audio(
                audio=open(file_path, 'rb'),
                title=title,
                performer=info.get('uploader', 'alexDownloader'),
                caption=f"✅ {title} downloaded successfully!",
                read_timeout=120,
                write_timeout=120
            )
        else:
            await update.message.reply_video(
                video=open(file_path, 'rb'),
                caption=f"✅ {title} downloaded successfully!",
                supports_streaming=True,
                read_timeout=120,
                write_timeout=120
            )

            
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
        await status_msg.delete()
        
    except Exception as e:
        logging.error(f"Bot error: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)[:100]}... Please check the URL or try again later.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).connect_timeout(60).read_timeout(60).write_timeout(60).build()

    
    start_handler = CommandHandler('start', start)
    download_handler = CommandHandler('download', download_cmd)
    audio_handler = CommandHandler('audio', audio_cmd)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(download_handler)
    application.add_handler(audio_handler)
    application.add_handler(message_handler)
    
    print("alexDownloader Bot is running...")
    application.run_polling()
