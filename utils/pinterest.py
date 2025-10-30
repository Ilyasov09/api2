import httpx
from bs4 import BeautifulSoup

async def download_pinterest_media(url: str):
    """
    Pinterest post yoki boarddan rasm va videolarni olish
    """
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise Exception("Pinterest URL not accessible")

        soup = BeautifulSoup(r.text, "html.parser")
        media_urls = []

        for img in soup.find_all("img"):
            if img.get("src"):
                media_urls.append(img["src"])
        for video in soup.find_all("video"):
            if video.get("src"):
                media_urls.append(video["src"])

        if not media_urls:
            raise Exception("No media found")
        return media_urls
