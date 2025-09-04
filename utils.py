import aiohttp
import os
import time
from aiohttp import web
from config import Config
from db import Database

routes = web.RouteTableDef()
START_TIME = time.time()

# --- Web server routes ---
@routes.get("/", allow_head=True)
async def root_route_handler(request):
    uptime = int(time.time() - START_TIME)
    return web.json_response({
        "status": "running",
        "bot": "UHD-MediaHost-Bot",
        "uptime_seconds": uptime,
        "admin": Config.ADMIN if getattr(Config, "ADMIN", None) else None
    })

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

# --- Upload to envs.sh ---
async def upload_to_envs(file_path: str, timeout: int = 120) -> str:
    """
    Uploads file to envs.sh. First tries PUT to https://envs.sh/<filename>, 
    then falls back to multipart POST if PUT fails.
    Returns the URL string on success, raises RuntimeError on failure.
    """
    filename = os.path.basename(file_path)
    put_url = f"https://envs.sh/{filename}"

    # Try PUT
    try:
        with open(file_path, "rb") as f:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.put(put_url, data=f, timeout=timeout) as resp:
                        text = await resp.text()
                        if resp.status in (200, 201):
                            return text.strip()
                except Exception:
                    pass
    except Exception as e:
        raise RuntimeError(f"Failed to open file for upload: {e}")

    # Fallback: multipart POST
    try:
        with open(file_path, "rb") as f:
            form = aiohttp.FormData()
            form.add_field("file", f, filename=filename, content_type="application/octet-stream")
            async with aiohttp.ClientSession() as session:
                async with session.post("https://envs.sh/", data=form, timeout=timeout) as resp:
                    text = await resp.text()
                    if resp.status in (200, 201):
                        return text.strip()
                    else:
                        raise RuntimeError(f"envs.sh POST failed with status {resp.status}")
    except Exception as e:
        raise RuntimeError(f"envs.sh upload failed: {e}")

# --- File cache helpers (for database) ---
async def save_file_cache(db: Database, msg):
    """
    Save media info into DB.files cache.
    """
    media = msg.document or msg.video or msg.audio or msg.photo
    if not media:
        return
    unique_id = getattr(media, "file_unique_id", None)
    file_id = getattr(media, "file_id", None)
    if unique_id and file_id:
        await db.cache_file(unique_id, file_id, file_ref=getattr(media, "file_ref", None))

async def get_cached_file(db: Database, unique_id: str):
    """
    Fetch cached file entry by unique_id.
    """
    return await db.get_cached(unique_id)
