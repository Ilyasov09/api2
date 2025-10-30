import os
from fastapi import FastAPI, HTTPException, Query
from utils.instagram import download_instagram_post
from utils.pinterest import download_pinterest_media

app = FastAPI(title="Media Downloader API")

# Instagram endpoint
@app.get("/instagram")
async def get_instagram(url: str = Query(..., description="Instagram post URL")):
    try:
        media = await download_instagram_post(url)
        return {"url": url, "media": media}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Pinterest endpoint
@app.get("/pinterest")
async def get_pinterest(url: str = Query(..., description="Pinterest pin URL")):
    try:
        media = await download_pinterest_media(url)
        return {"url": url, "media": media}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
