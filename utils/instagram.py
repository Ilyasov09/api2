import os
import httpx
from bs4 import BeautifulSoup
import json

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

async def download_instagram_post(url: str):
    """
    Instagram postdan rasm va videolarni yuklab oladi.
    """
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-CSRFToken": "missing",
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Login
        data = {"username": INSTAGRAM_USERNAME, "password": INSTAGRAM_PASSWORD}
        r = await client.post(login_url, data=data, headers=headers)
        if r.status_code != 200:
            raise Exception("Instagram login failed")

        # Postni olish
        r = await client.get(url, headers=headers)
        if r.status_code != 200:
            raise Exception("Instagram post not accessible")

        soup = BeautifulSoup(r.text, "html.parser")
        scripts = soup.find_all("script", type="text/javascript")
        media_urls = []

        for script in scripts:
            if "window._sharedData" in script.text:
                text = script.text.strip().replace("window._sharedData = ", "")[:-1]
                data = json.loads(text)
                try:
                    edges = data["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]
                    if "video_url" in edges:
                        media_urls.append(edges["video_url"])
                    if "display_url" in edges:
                        media_urls.append(edges["display_url"])
                except:
                    pass
        if not media_urls:
            raise Exception("No media found")
        return media_urls
