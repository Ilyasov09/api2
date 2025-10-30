import os
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip
import uuid
import shutil

# 🔐 Tokenni environment variable'dan olish
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN or ":" not in BOT_TOKEN:
    raise ValueError(
        "❌ BOT_TOKEN topilmadi yoki noto‘g‘ri formatda! "
        "Render environment variables’da BOT_TOKEN ni to‘g‘ri yozing."
    )

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Global o‘zgaruvchilar
video_file = None
folder_name = None


def get_pinterest_video(url: str):
    """Pinterest post sahifasidan video URL ni olish"""
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

        # Pinterest video linkini topamiz
        video_tag = soup.find("video")
        if video_tag and video_tag.get("src"):
            return video_tag["src"]

        meta_tag = soup.find("meta", property="og:video")
        if meta_tag and meta_tag.get("content"):
            return meta_tag["content"]

        return None
    except Exception as e:
        print("Xato:", e)
        return None


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        f"Salom, <b>{message.from_user.first_name}</b> 👋\n"
        "Men <b>Pinterest Downloader Bot</b>man!\n"
        "Menga Pinterest havolasini yubor — men video va audio tayyorlab beraman 🎬🎵",
    )


@bot.message_handler(func=lambda message: True)
def handle_link(message):
    global video_file, folder_name
    url = message.text.strip()

    if "pinterest.com" not in url:
        bot.reply_to(message, "Iltimos, Pinterest havolasini yuboring 🔗")
        return

    loader_msg = bot.send_message(message.chat.id, "⏳ Video yuklanmoqda, biroz kuting...")

    try:
        # Video linkni olish
        video_url = get_pinterest_video(url)
        if not video_url:
            bot.delete_message(message.chat.id, loader_msg.message_id)
            bot.reply_to(message, "❌ Video topilmadi.")
            return

        # Fayl nomi
        folder_name = str(uuid.uuid4())
        os.makedirs(folder_name, exist_ok=True)
        video_file = os.path.join(folder_name, "video.mp4")

        # Video yuklab olish
        with requests.get(video_url, stream=True) as r:
            with open(video_file, "wb") as f:
                shutil.copyfileobj(r.raw, f)

        bot.delete_message(message.chat.id, loader_msg.message_id)

        # Inline tugma — audio yuklash
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("🎵 Audioni yuklab olish", callback_data="get_audio")
        markup.add(btn)

        with open(video_file, "rb") as v:
            bot.send_video(message.chat.id, v, caption="🎬 Pinterest videosi", reply_markup=markup)

    except Exception as e:
        bot.delete_message(message.chat.id, loader_msg.message_id)
        bot.reply_to(message, f"⚠️ Xatolik yuz berdi: {e}")


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global video_file, folder_name
    if call.data == "get_audio":
        try:
            bot.send_message(call.message.chat.id, "🎧 Audioni ajratib olayapman...")

            video = VideoFileClip(video_file)
            audio = video.audio
            audio_name = os.path.join(folder_name, f"{uuid.uuid4()}.mp3")
            audio.write_audiofile(audio_name, verbose=False, logger=None)
            video.close()

            with open(audio_name, "rb") as a:
                bot.send_audio(call.message.chat.id, a, caption="🎵 Pinterest audiosi")

            os.remove(audio_name)

        except Exception as e:
            bot.reply_to(call.message, f"⚠️ Audio ajratishda xatolik: {e}")

        finally:
            if os.path.exists(folder_name):
                shutil.rmtree(folder_name, ignore_errors=True)


print("🤖 Pinterest bot ishga tushdi...")
bot.infinity_polling(skip_pending=True)
