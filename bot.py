import telebot
import requests
from bs4 import BeautifulSoup

# 🧩 Telegram bot token (BotFather dan olgan tokeningni shu yerga yoz)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# 🔍 Pinterest dan rasm/video URL ni olish funksiyasi
def get_pinterest_media(url: str):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # 🎬 Video bo‘lsa
        video_tag = soup.find("video")
        if video_tag and video_tag.get("src"):
            return ("video", video_tag["src"])

        # 🖼️ Rasm bo‘lsa
        meta_img = soup.find("meta", property="og:image")
        if meta_img and meta_img.get("content"):
            return ("image", meta_img["content"])

        return (None, None)
    except Exception as e:
        print("Xato:", e)
        return (None, None)

# 👋 /start komandasi
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        f"Salom, <b>{message.from_user.first_name}</b> 👋\n"
        "Men <b>Pinterest Downloader Bot</b>man!\n"
        "Menga Pinterest link yubor — men esa rasm yoki videoni yuboraman 📥"
    )

# 📎 Foydalanuvchi yuborgan Pinterest linkni qayta ishlash
@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text.strip()
    if "pinterest.com" not in url:
        bot.reply_to(message, "Iltimos, Pinterest havolasini yuboring 🔗")
        return

    bot.send_chat_action(message.chat.id, "typing")
    bot.reply_to(message, "🔎 Yuklanmoqda, biroz kuting...")

    media_type, media_url = get_pinterest_media(url)
    if not media_url:
        bot.reply_to(message, "❌ Media topilmadi yoki yuklab bo‘lmadi.")
        return

    if media_type == "video":
        bot.send_video(message.chat.id, media_url, caption="🎬 Pinterest videosi")
    elif media_type == "image":
        bot.send_photo(message.chat.id, media_url, caption="🖼️ Pinterest rasmi")
    else:
        bot.reply_to(message, "❌ Media formati noma'lum.")

# ▶️ Botni ishga tushirish
print("🤖 Bot ishga tushdi...")
bot.infinity_polling()
