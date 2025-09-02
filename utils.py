import aiohttp
import os
import time
from aiohttp import web
from config import Config

routes = web.RouteTableDef()
START_TIME = time.time()

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


async def upload_to_envs(file_path: str, timeout: int = 120) -> str:
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


# -----------------------------
# Log channel feature
# -----------------------------
async def send_log_message(bot, message: str):
    """
    Sends a log message to the configured LOG_CHANNEL.
    Usage: await send_log_message(bot, "Your message here")
    """
    if not getattr(Config, "LOG_CHANNEL", None):
        return
    try:
        await bot.send_message(chat_id=Config.LOG_CHANNEL, text=message)
    except Exception as e:
        print(f"Failed to send log message: {e}")
