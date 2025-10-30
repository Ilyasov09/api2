from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_pinterest_video(url: str) -> str | None:
    """Pinterest post sahifasidan video URL ni ajratib olish."""
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

        # Pinterest videolari <video> yoki meta property orqali keladi
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

@app.route("/")
def index():
    return jsonify({
        "message": "✅ Pinterest Video Downloader API (Python 3.13.4)",
        "usage": "POST /api/download { 'url': '<pinterest_link>' }"
    })

@app.route("/api/download", methods=["POST"])
def download_video():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "URL yuborilmadi"}), 400

    video_url = get_pinterest_video(data["url"])
    if not video_url:
        return jsonify({"error": "Video topilmadi"}), 404

    return jsonify({"download_url": video_url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
